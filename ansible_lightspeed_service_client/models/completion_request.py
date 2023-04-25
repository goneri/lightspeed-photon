from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import Union

import attr

from ..types import UNSET
from ..types import Unset

if TYPE_CHECKING:
    from ..models.metadata import Metadata


T = TypeVar("T", bound="CompletionRequest")


@attr.s(auto_attribs=True)
class CompletionRequest:
    """
    Attributes:
        prompt (str): Editor prompt.
        suggestion_id (Union[Unset, str]): A UUID that identifies a suggestion.
        metadata (Union[Unset, Metadata]):
    """

    prompt: str
    suggestion_id: Union[Unset, str] = UNSET
    metadata: Union[Unset, "Metadata"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        prompt = self.prompt
        suggestion_id = self.suggestion_id
        metadata: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "prompt": prompt,
            }
        )
        if suggestion_id is not UNSET:
            field_dict["suggestionId"] = suggestion_id
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.metadata import Metadata

        d = src_dict.copy()
        prompt = d.pop("prompt")

        suggestion_id = d.pop("suggestionId", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: Union[Unset, Metadata]
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = Metadata.from_dict(_metadata)

        completion_request = cls(
            prompt=prompt,
            suggestion_id=suggestion_id,
            metadata=metadata,
        )

        completion_request.additional_properties = d
        return completion_request

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
