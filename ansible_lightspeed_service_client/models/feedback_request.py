import json
from typing import Any
from typing import Dict
from typing import List
from typing import Tuple
from typing import Type
from typing import TYPE_CHECKING
from typing import TypeVar
from typing import Union

import attr

from ..types import UNSET
from ..types import Unset

if TYPE_CHECKING:
    from ..models.ansible_content_feedback import AnsibleContentFeedback
    from ..models.inline_suggestion_feedback import InlineSuggestionFeedback


T = TypeVar("T", bound="FeedbackRequest")


@attr.s(auto_attribs=True)
class FeedbackRequest:
    """
    Attributes:
        inline_suggestion (Union[Unset, InlineSuggestionFeedback]):
        ansible_content (Union[Unset, AnsibleContentFeedback]):
    """

    inline_suggestion: Union[Unset, "InlineSuggestionFeedback"] = UNSET
    ansible_content: Union[Unset, "AnsibleContentFeedback"] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        inline_suggestion: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.inline_suggestion, Unset):
            inline_suggestion = self.inline_suggestion.to_dict()

        ansible_content: Union[Unset, Dict[str, Any]] = UNSET
        if not isinstance(self.ansible_content, Unset):
            ansible_content = self.ansible_content.to_dict()

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if inline_suggestion is not UNSET:
            field_dict["inlineSuggestion"] = inline_suggestion
        if ansible_content is not UNSET:
            field_dict["ansibleContent"] = ansible_content

        return field_dict

    def to_multipart(self) -> Dict[str, Any]:
        inline_suggestion: Union[Unset, Tuple[None, bytes, str]] = UNSET
        if not isinstance(self.inline_suggestion, Unset):
            inline_suggestion = (
                None,
                json.dumps(self.inline_suggestion.to_dict()).encode(),
                "application/json",
            )

        ansible_content: Union[Unset, Tuple[None, bytes, str]] = UNSET
        if not isinstance(self.ansible_content, Unset):
            ansible_content = (
                None,
                json.dumps(self.ansible_content.to_dict()).encode(),
                "application/json",
            )

        field_dict: Dict[str, Any] = {}
        field_dict.update(
            {
                key: (None, str(value).encode(), "text/plain")
                for key, value in self.additional_properties.items()
            }
        )
        field_dict.update({})
        if inline_suggestion is not UNSET:
            field_dict["inlineSuggestion"] = inline_suggestion
        if ansible_content is not UNSET:
            field_dict["ansibleContent"] = ansible_content

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        from ..models.ansible_content_feedback import AnsibleContentFeedback
        from ..models.inline_suggestion_feedback import InlineSuggestionFeedback

        d = src_dict.copy()
        _inline_suggestion = d.pop("inlineSuggestion", UNSET)
        inline_suggestion: Union[Unset, InlineSuggestionFeedback]
        if isinstance(_inline_suggestion, Unset):
            inline_suggestion = UNSET
        else:
            inline_suggestion = InlineSuggestionFeedback.from_dict(_inline_suggestion)

        _ansible_content = d.pop("ansibleContent", UNSET)
        ansible_content: Union[Unset, AnsibleContentFeedback]
        if isinstance(_ansible_content, Unset):
            ansible_content = UNSET
        else:
            ansible_content = AnsibleContentFeedback.from_dict(_ansible_content)

        feedback_request = cls(
            inline_suggestion=inline_suggestion,
            ansible_content=ansible_content,
        )

        feedback_request.additional_properties = d
        return feedback_request

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
