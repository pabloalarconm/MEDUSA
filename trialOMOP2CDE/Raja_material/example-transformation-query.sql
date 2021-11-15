SELECT person_id, make_date(year_of_birth,month_of_birth,day_of_birth) AS dob, gender_concept_id , cde_sex(gender_concept_id) AS sex FROM testomop.person
