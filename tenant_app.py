from portals.TenantPortal import TenantPortal


def main():
    try:
        tenant_portal = TenantPortal()
        tenant_portal.start()
    except Exception as e:
        print("An error has occurred: {}".format(e))


if __name__ == "__main__":
    main()