from backend.custom_tools.queryPDL import PDLHandler


def queryTest():
    success, response = PDLHandler.sendQuery(PDLHandler.ES_QUERY, 1)
    assert success == True
    assert len(response["data"]) == 1

    profile = response["data"][0]
    expected_response_full_name = "rascator tran"
    expected_response_mobile_phone = "+84904333302"
    actual_response_full_name = profile["full_name"]
    actual_response_mobile_phone = profile["mobile_phone"]
    assert actual_response_full_name == expected_response_full_name
    assert actual_response_mobile_phone == actual_response_mobile_phone


if __name__ == "__main__":
    queryTest()
