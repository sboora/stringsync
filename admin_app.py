from portals.AdminPortal import AdminPortal


def main():
    try:
        admin_portal = AdminPortal()
        admin_portal.start()
    except Exception as e:
        print("An error has occurred: {}".format(e))


if __name__ == "__main__":
    main()
