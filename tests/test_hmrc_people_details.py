from table_hmrc_people_details import HMRC_PeopleDetails


def test_people():
    people = HMRC_PeopleDetails()
    print(people.fetch_all())
    print(people.fetch_by_code("B"))

    person_code = "S"
    person = HMRC_PeopleDetails(person_code)
    name = person.get_name()

    print(f"Person '{person_code}' is '{name}'")
    print(f"Person '{person_code}' was born '{person.get_date_of_birth()}'")
    print(f"Person '{person_code}' has phone number '{person.get_phone_number()}'")
    print(
        f"Person '{person_code}' has NI number '{person.get_national_insurance_number()}'"
    )
    print(f"Person '{person_code}' has UTR '{person.get_unique_tax_reference()}'")
    print(f"Person '{person_code}' has spouse code '{person.get_spouse_code()}'")
    print(
        f"Person '{person_code}' has UTR check digit '{person.get_utr_check_digit()}'"
    )
    assert people.get_how_many() == 2  # Ian & Ian


test_people()
