from walking_on_sunshine.command.root import root_cmd


def main():
    try:
        root_cmd()
    except Exception:
        print("Oh no")


if __name__ == "__main__":
    main()
