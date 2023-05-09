from backend.custom_tools.queryPDL import PDLHandler


def queryTest():
    success, response = PDLHandler.sendQuery(PDLHandler.ES_QUERY, 1)
    assert success == True
    assert len(response["data"]) == 1

    profile = response["data"][0]
    actual_response_full_name = profile["full_name"]
    actual_response_mobile_phone = profile["mobile_phone"]
    assert len(actual_response_full_name) > 0


if __name__ == "__main__":
    queryTest()
