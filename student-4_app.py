from portals.StudentPortal import StudentPortal


def main():
    student_portal = StudentPortal()
    student_portal.start(register=True)


if __name__ == "__main__":
    main()
