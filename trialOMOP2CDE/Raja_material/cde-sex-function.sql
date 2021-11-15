CREATE FUNCTION cde_sex(sex integer) RETURNS text AS $$
        BEGIN
                IF sex = 8532 THEN
                   RETURN 'http://purl.obolibrary.org/obo/NCIT_C16576';
                ELSEIF sex = 8507 THEN
                   RETURN 'http://purl.obolibrary.org/obo/NCIT_C20197';
                ELSEIF sex = 9999 THEN
                   RETURN 'http://purl.obolibrary.org/obo/NCIT_C124294';
                ELSE
                   RETURN 'http://purl.obolibrary.org/obo/NCIT_C17998';
		 END IF;
        END;
$$ LANGUAGE plpgsql;
