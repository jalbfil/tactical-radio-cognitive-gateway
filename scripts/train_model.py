from tactical_radio_gateway.ml_classifier import train_classifier

def main() -> None:
    model = train_classifier()
    print('Synthetic classifier trained successfully.')
    print(model)
if __name__ == '__main__': main()
