from class_defs import Person


if __name__ == "__main__":
    # Create a test person (you can change these values)
    test_person = Person(
        user_id=1,
        email="test@example.com",
        name="Test User",
        memtype="Gold",
        phone="555-1234",
        address_id=101,
        login_id=999
    )

    # Get the class table for this person
    print("Fetching class table for test person:")
    test_person.get_class_table()