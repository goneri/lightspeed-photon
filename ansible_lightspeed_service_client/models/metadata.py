from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

import attr

from ..types import UNSET
from ..types import Unset

T = TypeVar("T", bound="Metadata")


@attr.s(auto_attribs=True)
class Metadata:
    """
    Attributes:
        document_uri (Union[Unset, str]):
        activity_id (Union[Unset, str]): A UUID that identifies a user activity session within a given document.
    """

    document_uri: Union[Unset, str] = UNSET
    activity_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        document_uri = self.document_uri
        activity_id = self.activity_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if document_uri is not UNSET:
            field_dict["documentUri"] = document_uri
        if activity_id is not UNSET:
            field_dict["activityId"] = activity_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        document_uri = d.pop("documentUri", UNSET)

        activity_id = d.pop("activityId", UNSET)

        metadata = cls(
            document_uri=document_uri,
            activity_id=activity_id,
        )

        metadata.additional_properties = d
        return metadata

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
