import csv

CARDS_CSV = "./input/cards.csv"
STATEMENT_DIR = "./input/"


def get_cards(cards_csv_path: str):
    out = []
    with open(cards_csv_path) as config_file:
        config_reader = csv.reader(config_file)
        next(config_reader)  # skip header
        for row in config_reader:
            out.append({"card_no": row[0], "card_name": row[1]})

    return out


cards = get_cards(CARDS_CSV)
print(cards[0]['card_no'])
#print(cards[0].card_no, cards[0].card_name)
