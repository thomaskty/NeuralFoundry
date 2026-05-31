from pprint import pprint
def debug_agent_response(response: dict):

    print("\n" + "=" * 120)
    print("AGENT RESPONSE")
    print("=" * 120)

    messages = response.get("messages", [])

    for idx, message in enumerate(messages, start=1):

        print("\n" + "-" * 120)
        print(f"MESSAGE #{idx}")
        print("-" * 120)

        print(f"TYPE      : {message.__class__.__name__}")
        print(f"ID        : {getattr(message, 'id', None)}")

        content = getattr(message, "content", None)

        print("\nCONTENT:")
        print(content)

        additional_kwargs = getattr(
            message,
            "additional_kwargs",
            {}
        )

        if additional_kwargs:
            print("\nADDITIONAL_KWARGS:")
            pprint(additional_kwargs)

        response_metadata = getattr(
            message,
            "response_metadata",
            {}
        )

        if response_metadata:
            print("\nRESPONSE_METADATA:")
            pprint(response_metadata)

        usage_metadata = getattr(
            message,
            "usage_metadata",
            None
        )

        if usage_metadata:
            print("\nUSAGE_METADATA:")
            pprint(usage_metadata)

        tool_calls = getattr(
            message,
            "tool_calls",
            None
        )

        if tool_calls:
            print("\nTOOL_CALLS:")
            pprint(tool_calls)

        invalid_tool_calls = getattr(
            message,
            "invalid_tool_calls",
            None
        )

        if invalid_tool_calls:
            print("\nINVALID_TOOL_CALLS:")
            pprint(invalid_tool_calls)

    print("\n" + "=" * 120)