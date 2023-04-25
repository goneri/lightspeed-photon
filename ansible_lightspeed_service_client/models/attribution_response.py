from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar

import attr

if TYPE_CHECKING:
    from ..models.attribution import Attribution


T = TypeVar("T", bound="AttributionResponse")


@attr.s(auto_attribs=True)
class AttributionResponse:
    """
    Attributes:
        attributions (List['Attribution']):
    """

    attributions: List["Attribution"]
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        attributions = []
        for attributions_item_data in self.attributions:
            attributions_item = attributions_item_data.to_dict()

            attributions.append(attributions_item)

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "attributions": attributions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.attribution import Attribution

        d = src_dict.copy()
        attributions = []
        _attributions = d.pop("attributions")
        for attributions_item_data in _attributions:
            attributions_item = Attribution.from_dict(attributions_item_data)

            attributions.append(attributions_item)

        attribution_response = cls(
            attributions=attributions,
        )

        attribution_response.additional_properties = d
        return attribution_response

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
