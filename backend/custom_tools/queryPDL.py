import json
import os
from dotenv import load_dotenv
import pdb
from typing import Dict, List
import plotly.express as px
import plotly.graph_objects as go

load_dotenv()


def printProfileNicely(profile: Dict):
    for key, value in profile.items():
        print(f"{key}: {value}")


# See https://github.com/peopledatalabs/peopledatalabs-python
from peopledatalabs import PDLPY


class PDLHandler:
    # Create a client, specifying your API key
    CLIENT = PDLPY(
        api_key=os.environ["PDL_API_KEY"],
    )

    # Create an Elasticsearch query
    ES_QUERY = {
        "query": {
            "bool": {
                "must": [
                    {"term": {"location_country": "vietnam"}},
                    {"term": {"job_company_location_country": "vietnam"}},
                    {"match": {"skills": "javascript"}},
                ],
                "should": [
                    {"exists": {"field": "phone_numbers"}},
                ],
            }
        }
    }

    @classmethod
    def sendQuery(cls, esQuery=ES_QUERY, batchSize: int = 1):
        # Create a parameters JSON object
        PARAMS = {"query": esQuery, "size": batchSize, "pretty": True}

        # Pass the parameters object to the Person Search API
        response = PDLHandler.CLIENT.person.search(**PARAMS).json()
        # Check for successful response
        if response["status"] == 200:
            data = response["data"]
            # Write out each profile found to file
            with open("my_pdl_search.jsonl", "w") as out:
                for record in data:
                    out.write(json.dumps(record) + "\n")
            print(f"Successfully grabbed {len(data)} records from PDL.")
            print(f"{response['total']} total PDL records exist matching this query.")
            # Print candidates
            for record in data:
                print(f"--> Candidate:")
                PDLHandler.extractProfileBasedOnClauses(record)
            return True, response

        else:
            print(
                "NOTE: The carrier pigeons lost motivation in flight. See error and try again."
            )
            print("Error:", response)
            return False, ""

    @classmethod
    def buildQuery(cls, must_clauses: List[str], should_clauses: List[str]):
        query = {"query": {"bool": {"must": must_clauses, "should": should_clauses}}}
        return query

    @classmethod
    def analyze_criteria(cls, query_es: ES_QUERY):
        import matplotlib.pyplot as plt

        individual_totals = []
        joint_totals = []

        must_clauses = query_es["query"]["bool"]["must"]
        should_clauses = query_es["query"]["bool"]["should"]

        # Individual Clauses
        print("Individual Clause Demographics")
        for idx in range(len(must_clauses)):
            m_clauses = must_clauses[idx]
            s_clauses = []
            query_individual = {
                "query": {"bool": {"must": m_clauses, "should": s_clauses}}
            }

            success, results = PDLHandler.sendQuery(query_individual, 1)
            individual_totals.append(results["total"])
            print(f"{idx+1}) Total Count: {results['total']} - Criteria: {m_clauses}")

        x_range = range(1, len(must_clauses) + 1)
        x_range2 = range(len(must_clauses) + 1)

        # Joint Clauses
        print("\nJoint Clause Demographics")
        for idx in range(len(must_clauses) + 1):
            m_clauses = must_clauses[:idx]
            s_clauses = []
            query_joint = {"query": {"bool": {"must": m_clauses, "should": s_clauses}}}

            success, results = PDLHandler.sendQuery(query_joint, 1)
            joint_totals.append(results["total"])
            print(
                f"{idx}) "
                f"Total Count: {results['total']} - "
                f"Criteria: {m_clauses[-1] if idx else {}}"
            )

        # Plot individual totals as histogram and joint totals as line
        x = list(x_range)
        x2 = list(x_range2)

        labels = [f"criteria_{i}" for i in x]
        labels2 = [f"criteria_{i}" for i in x2]
        title = "Criteria Testing"

        fig = go.Figure()
        fig.add_bar(x=x, y=individual_totals, name="Individual Clause Totals")
        fig.add_trace(
            go.Scatter(x=x2, y=joint_totals, name="Joint Clause Totals", mode="lines")
        )
        fig.update_layout(
            title=title,
            xaxis=dict(
                tickmode="array", tickvals=x2, ticktext=labels2, title="Criteria ID"
            ),
            yaxis=dict(title="Total Number of Profile Matches"),
            showlegend=True,
            height=700,
        )
        fig.data[0].name = "Joint Clause Total"
        fig.update_yaxes(type="log")
        fig.show()

    @classmethod
    def extractProfileBasedOnClauses(
        cls, profile: Dict, must_clauses: List = [], should_clauses: List = []
    ):
        print_field_names = [
            "full_name",
            "personal_emails",
            "mobile_phone",
            "linkedin_url",
            "location_country",
            "skills",
        ]

        print_field_values = []
        for field_name in print_field_names:
            field_value = profile[field_name]
            if field_name == "personal_emails" and len(field_value) == 0:
                field_value = profile["work_email"]
            print_field_values.append(field_value)

        # Get past companies
        experience_companies = []
        for exp in profile["experience"]:
            company = exp["company"]["name"]
            experience_companies.append(exp)

        for clause in must_clauses:
            criteria = clause.keys()[0]
            field_name = criteria.keys()[0]
            if (
                field_name != "field"
                and criteria != "exists"
                and field_name not in print_field_names
            ):
                field_value = profile[field_name]
                print_field_names.append(field_name)
                print_field_values.append(field_value)

        for clause in should_clauses:
            criteria = clause.keys()[0]
            field_name = criteria.keys()[0]
            if (
                field_name != "field"
                and criteria != "exists"
                and field_name not in print_field_names
            ):
                field_value = profile[field_name]
                print_field_names.append(field_name)
                print_field_values.append(field_value)

        # TODO: remove
        for i in range(len(print_field_names)):
            print(f"{print_field_names[i]}: {print_field_values[i]}")
        return print_field_names, print_field_values


if __name__ == "__main__":
    PDLHandler.sendQuery(PDLHandler.ES_QUERY, 1)
    PDLHandler.analyze_criteria(PDLHandler.ES_QUERY)
