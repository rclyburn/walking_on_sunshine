from walking_on_sunshine.command.root import root_cmd


def main():
    try:
        root_cmd()
    except Exception as e:
        raise e


if __name__ == "__main__":
    main()
