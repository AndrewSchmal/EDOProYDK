import requests
import re
import os

def get_card_id(card_name, format_name=None):
    """
    Convert a card name to its Konami ID using YGOProDeck API.
    Includes format restriction if provided.
    """
    try:
        url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?name={card_name}"
        if format_name:
            url += f"&format={format_name}"  # Append the format parameter
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return str(data['data'][0]['id'])  # Return the ID as a string
        else:
            print(f"Card '{card_name}' not found or not legal in format '{format_name}'.")
            return None
    except Exception as e:
        print(f"Error fetching ID for '{card_name}': {e}")
        return None

def parse_deck_list(deck_list, format_name=None):
    """
    Parse a deck list from formatted input text, considering the chosen format.
    """
    main_deck, extra_deck, side_deck = [], [], []
    current_section = "main"  # Default section is 'main'

    # Flexible regex for matching quantities and card names
    card_regex = re.compile(r"^(?:\s*(\d+)[xX]?\s*|\s*[xX](\d+)\s*)(.+)$")

    for line in deck_list.splitlines():
        line = line.strip()  # Remove leading/trailing spaces
        if not line:  # Skip empty lines
            continue

        # Detect section headers
        if line.lower() == "#main":
            current_section = "main"
        elif line.lower() == "#extra":
            current_section = "extra"
        elif line.lower() == "#side":
            current_section = "side"
        else:
            # Match the card line to the regex
            match = card_regex.match(line)
            if match:
                quantity = int(match.group(1) or match.group(2))  # Get the quantity
                card_name = match.group(3).strip()  # Get the card name

                # Convert card name to ID, considering format
                card_id = get_card_id(card_name, format_name)
                if card_id:
                    # Add card ID quantity times to the appropriate deck
                    for _ in range(quantity):
                        if current_section == "main":
                            main_deck.append(card_id)
                        elif current_section == "extra":
                            extra_deck.append(card_id)
                        elif current_section == "side":
                            side_deck.append(card_id)
    return main_deck, extra_deck, side_deck

def write_ydk_file(output_path, main_deck, extra_deck, side_deck):
    """
    Write parsed decks to a .YDK file.
    """
    with open(output_path, "w") as file:
        file.write("#main\n")
        file.write("\n".join(main_deck) + "\n")
        if extra_deck:
            file.write("\n#extra\n")
            file.write("\n".join(extra_deck) + "\n")
        if side_deck:
            file.write("\n!side\n")
            file.write("\n".join(side_deck) + "\n")

def main():
    # Prompt the user to select a format
    print("Select the format you are playing (leave blank for no restriction):")
    print("Examples: 'GOAT', 'Modern', 'TCG', 'OCG'.")
    format_name = input("Enter format (or press Enter for no restriction): ").strip()

    # Prompt user to input the deck list
    print("\nEnter your deck list. Use '#main', '#extra', and '#side' headers for sections.")
    print("Examples of valid inputs:")
    print("  '1x Pot of Greed'")
    print("  'x1 Pot of Greed'")
    print("  '1 Pot of Greed'")
    print("Leave '#extra' and '#side' sections empty if you don't have cards for those.")
    print("When you're done, type 'DONE' (case insensitive) to finish.")
    print("-" * 50)

    # Read deck list input from the user
    deck_list = []
    while True:
        line = input()
        if line.strip().lower() == "done":
            break
        deck_list.append(line)
    deck_list = "\n".join(deck_list)

    # Ask the user for the output file name
    print("\nEnter the name of the YDK file you want to create (spaces allowed):")
    file_name = input().strip()
    if not file_name.endswith(".ydk"):
        file_name += ".ydk"

    # Process deck list and write YDK file
    main_deck, extra_deck, side_deck = parse_deck_list(deck_list, format_name)
    output_path = os.path.abspath(file_name)
    write_ydk_file(output_path, main_deck, extra_deck, side_deck)

    # Notify the user of the file location
    print(f"\nYDK file created at: {output_path}")

if __name__ == "__main__":
    main()
