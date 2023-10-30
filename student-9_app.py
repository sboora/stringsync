from portals.StudentPortal import StudentPortal


def main():
    try:
        student_portal = StudentPortal()
        student_portal.start(register=True)
    except Exception as e:
        print("An error has occurred: {}".format(e))


if __name__ == "__main__":
    main()
