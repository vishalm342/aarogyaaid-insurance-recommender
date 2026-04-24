def test_recommendation_suitability():
    # Mock data for unit test
    profile = {
        "pre_existing_conditions": ["Diabetes"],
        "annual_income": "under_3L"
    }
    
    policy_a = {
        "co_pay": "5%",
        "diabetes_exclusion": False,
        "score": 0
    }
    
    policy_b = {
        "co_pay": "10%",
        "diabetes_exclusion": True,
        "score": 0
    }
    
    # Simple scoring logic
    def score_policy(p, prof):
        score = 50
        if "Diabetes" in prof["pre_existing_conditions"]:
            if p["diabetes_exclusion"]:
                score -= 30
            else:
                score += 20
        if prof["annual_income"] == "under_3L":
            if p["co_pay"] == "5%":
                score += 10
            else:
                score -= 5
        return score
        
    policy_a["score"] = score_policy(policy_a, profile)
    policy_b["score"] = score_policy(policy_b, profile)
    
    assert policy_a["score"] > policy_b["score"], "Policy without diabetes exclusion should score higher"
    assert policy_a["score"] == 80
    assert policy_b["score"] == 15