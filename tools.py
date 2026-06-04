from langchain_core.tools import tool


@tool
def priority_calculator_tool(text: str) -> str:
    """
    Calculates incident priority
    based on incident keywords.
    """

    try:

        text = text.lower()

        if any(
            word in text
            for word in ["critical", "urgent", "harassment"]
        ):
            return "Critical"

        elif any(
            word in text
            for word in [
                "vpn",
                "server",
                "system",
                "salary"
            ]
        ):
            return "High"

        elif any(
            word in text
            for word in [
                "leave",
                "portal",
                "password"
            ]
        ):
            return "Medium"

        return "Low"

    except Exception as e:

        return f"Tool Error: {str(e)}"


if __name__ == "__main__":

    result = priority_calculator_tool.invoke(
        "Urgent VPN outage"
    )

    print(result)