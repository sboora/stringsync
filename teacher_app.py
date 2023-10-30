from portals.TeacherPortal import TeacherPortal


def main():
    try:
        teacher_portal = TeacherPortal()
        teacher_portal.start()
    except Exception as e:
        print("An error has occurred: {}".format(e))


if __name__ == "__main__":
    main()
