from korean_maritime_law_rag.agent.state import AgentResponse, GeneratedAnswer, VerifiedAnswer


def test_agent_state_list_fields_use_default_factory():
    assert GeneratedAnswer.model_fields["citations"].default_factory is list
    assert VerifiedAnswer.model_fields["valid_citations"].default_factory is list
    assert VerifiedAnswer.model_fields["invalid_citations"].default_factory is list
    assert AgentResponse.model_fields["citations"].default_factory is list
