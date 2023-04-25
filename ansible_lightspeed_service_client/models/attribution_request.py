from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

import attr

from ..types import UNSET
from ..types import Unset

T = TypeVar("T", bound="AttributionRequest")


@attr.s(auto_attribs=True)
class AttributionRequest:
    """
    Attributes:
        suggestion (str):
        suggestion_id (Union[Unset, str]): A UUID that identifies the particular suggestion attribution data is being
            requested for.
    """

    suggestion: str
    suggestion_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        suggestion = self.suggestion
        suggestion_id = self.suggestion_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "suggestion": suggestion,
            }
        )
        if suggestion_id is not UNSET:
            field_dict["suggestionId"] = suggestion_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        suggestion = d.pop("suggestion")

        suggestion_id = d.pop("suggestionId", UNSET)

        attribution_request = cls(
            suggestion=suggestion,
            suggestion_id=suggestion_id,
        )

        attribution_request.additional_properties = d
        return attribution_request

    @property
    def additional_keys(self) -> List[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
