import datetime

import pytest

from pydo import fulids


@pytest.fixture
def fulid():
    yield fulids.fulid()


class Testfulid:
    """
    Test class to ensure that the fulid object generates the ulids as we
    expect.
    """

    def test_representation(self, fulid):
        fulid.new()
        assert str(
            fulid.__repr__
        ) == "<bound method fulid.__repr__ of" + " <fulid('{}')>>".format(fulid.str)

    def test_fulid_has_charset_attribute(self, config, fulid):
        assert fulid.charset == list(config.get("fulid.characters"))

    def test_fulid_has_forbidden_charset_attribute(self, config, fulid):
        assert fulid.forbidden_charset == list(config.get("fulid.forbidden_characters"))

    def test_fulid_has_fulid_attribute_none_by_default(self, fulid):
        assert fulid.str is None

    def test_fulid_has_charset_attribute_set_by_default(self, config, fulid):
        assert fulid.charset == list(config.get("fulid.characters"))

    def test_fulid_has_forbidden_charset_attribute_set_by_default(self, config, fulid):
        assert fulid.forbidden_charset == list(config.get("fulid.forbidden_characters"))

    def test_fulid_can_set_fulid_attribute(self):
        fulid = fulids.fulid(fulid="full_fulid_string")
        assert fulid.str == "full_fulid_string"

    def test_fulid_can_set_charset_attribute(self):
        fulid = fulids.fulid(character_set="ab")
        assert fulid.charset == ["a", "b"]

    def test_fulid_can_set_forbidden_charset_attribute(self):
        fulid = fulids.fulid(forbidden_charset="/")
        assert fulid.forbidden_charset == ["/"]

    def test_fulid_returns_timestamp(self, fulid):
        fulid.new()
        assert isinstance(fulid.timestamp(), datetime.datetime)

    def test_fulid_returns_randomness(self, fulid):
        fulid.new()
        assert fulid.randomness() == fulid.str[10:19]

    def test_fulid_returns_id(self, fulid):
        fulid.new()
        assert fulid.id() == fulid.str[19:]

    def test_fulid_new_generates_an_fulid_object(self, fulid):
        id = fulid.new()
        assert isinstance(id, fulids.fulid)

    def test_fulid_generates_an_ulid_with_the_id_in_charset(self, config, fulid):
        for character in fulid.new().id():
            assert character.lower() in config.get("fulid.characters")

    def test_fulid_does_not_accept_invalid_terminal_characters(self, config, fulid):
        with pytest.raises(ValueError):
            fulids.fulid(
                "ilou|&:;()<>~*@?!$#[]{}\\/'\"`",
                config.get("fulid.forbidden_characters"),
            )

    def test_fulid_sets_the_fulid_attribute(self, fulid):
        fulid = fulid.new()
        assert len(fulid.str) == 26
        assert isinstance(fulid.str, str)

    def test_fulid_new_returns_first_fulid_if_last_fulid_is_none(self, fulid):
        assert fulid.new().id() == "AAAAAAA"

    def test_fulid_from_str_generates_fulid(self, fulid):
        assert isinstance(fulid.from_str("01DW02J8WWJNB109DA0AAAAAAA"), fulids.fulid)

    def test_string_to_number_can_decode_number(self, fulid):
        assert fulid._decode_id("AAAAAAA") == 0
        assert fulid._decode_id("RRRRRRR") == 9999999

    def test_string_to_number_can_decode_fulid_id(self, fulid):
        assert fulid._decode_id("01DW02J8WWJNB109DA0AAAAAAA") == 0

    def test_string_to_number_raises_error_if_char_not_in_charset(self, fulid):
        with pytest.raises(ValueError):
            # 7 is not in the charset
            fulid._decode_id("7")

    def test_encode_number_returns_expected_string(self, fulid):
        assert fulid._encode_id(0) == "A"
        assert fulid._encode_id(999999) == "RRRRRR"

    def test_encode_number_supports_padding(self, fulid):
        assert fulid._encode_id(0, 7) == "AAAAAAA"
        assert fulid._encode_id(2, 7) == "AAAAAAD"

    def test_encode_number_supports_base_different_than_10(self, fulid):
        fulid.charset = ["a", "s"]
        assert fulid._encode_id(0) == "A"
        assert fulid._encode_id(2) == "SA"

    def test_fulid_new_returns_sequential_id(self, fulid):
        assert fulid.new("01DW02J8WWJNB109DA0AAAAAAA").id() == "AAAAAAS"

    def test_short_fulids_returns_one_character_if_no_coincidence(self, fulid):
        fulids = [
            "01DWF3DM7EH40BTYB4SAAAAAAA",
            "01DWF3ETGBK679178BNAAAAAAS",
            "01DWF3EZYE0ANTCMCSSAAAAAAD",
        ]
        expected_sulids = {
            "01DWF3DM7EH40BTYB4SAAAAAAA": "a",
            "01DWF3ETGBK679178BNAAAAAAS": "s",
            "01DWF3EZYE0ANTCMCSSAAAAAAD": "d",
        }
        assert fulid.sulids(fulids) == expected_sulids

    def test_short_fulids_returns_two_characters_if_coincidence_in_first(self, fulid):
        fulids = [
            "01DWF3DM7EH40BTYB4SAAAAAAA",
            "01DWF3ETGBK679178BNAAAAASA",
            "01DWF3EZYE0ANTCMCSSAAAAAAD",
        ]
        expected_sulids = {
            "01DWF3DM7EH40BTYB4SAAAAAAA": "aa",
            "01DWF3ETGBK679178BNAAAAASA": "sa",
            "01DWF3EZYE0ANTCMCSSAAAAAAD": "ad",
        }
        assert fulid.sulids(fulids) == expected_sulids

    def test_expand_sulid_returns_fulid_if_no_coincidence(self, fulid):
        fulids = [
            "01DWF3DM7EH40BTYB4SAAAAAAA",
            "01DWF3ETGBK679178BNAAAAAAS",
            "01DWF3EZYE0ANTCMCSSAAAAAAD",
        ]
        assert fulid.sulid_to_fulid("a", fulids) == "01DWF3DM7EH40BTYB4SAAAAAAA"

    def test_expand_sulid_errors_if_there_is_more_than_one_coincidence(self, fulid):
        fulids = [
            "01DWF3DM7EH40BTYB4SAAAAAAA",
            "01DWF3ETGBK679178BNAAAAASA",
            "01DWF3EZYE0ANTCMCSSAAAAAAD",
        ]
        with pytest.raises(KeyError):
            fulid.sulid_to_fulid("a", fulids)

    def test_contract_fulid_returns_sulid(self, fulid):
        fulids = [
            "01DWF3DM7EH40BTYB4SAAAAAAA",
            "01DWF3ETGBK679178BNAAAAAAS",
            "01DWF3EZYE0ANTCMCSSAAAAAAD",
        ]
        assert fulid.fulid_to_sulid(fulids[0], fulids) == "a"

    def test_contract_ulid_errors_if_not_found(self, fulid):
        fulids = [
            "01DWF3DM7EH40BTYB4SAAAAAAA",
            "01DWF3ETGBK679178BNAAAAASA",
            "01DWF3EZYE0ANTCMCSSAAAAAAD",
        ]
        with pytest.raises(KeyError):
            fulid.fulid_to_sulid("non_existent", fulids)
