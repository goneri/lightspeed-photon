from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

import attr

from ..models.action_enum import ActionEnum
from ..types import UNSET
from ..types import Unset

T = TypeVar("T", bound="InlineSuggestionFeedback")


@attr.s(auto_attribs=True)
class InlineSuggestionFeedback:
    """
    Attributes:
        action (ActionEnum):
        suggestion_id (str): A UUID that identifies a suggestion.
        latency (Union[Unset, float]):
        user_action_time (Union[Unset, float]):
        document_uri (Union[Unset, str]):
        error (Union[Unset, str]):
        activity_id (Union[Unset, str]): A UUID that identifies a user activity session to the document uploaded.
    """

    action: ActionEnum
    suggestion_id: str
    latency: Union[Unset, float] = UNSET
    user_action_time: Union[Unset, float] = UNSET
    document_uri: Union[Unset, str] = UNSET
    error: Union[Unset, str] = UNSET
    activity_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        action = self.action.value

        suggestion_id = self.suggestion_id
        latency = self.latency
        user_action_time = self.user_action_time
        document_uri = self.document_uri
        error = self.error
        activity_id = self.activity_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "action": action,
                "suggestionId": suggestion_id,
            }
        )
        if latency is not UNSET:
            field_dict["latency"] = latency
        if user_action_time is not UNSET:
            field_dict["userActionTime"] = user_action_time
        if document_uri is not UNSET:
            field_dict["documentUri"] = document_uri
        if error is not UNSET:
            field_dict["error"] = error
        if activity_id is not UNSET:
            field_dict["activityId"] = activity_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        action = ActionEnum(d.pop("action"))

        suggestion_id = d.pop("suggestionId")

        latency = d.pop("latency", UNSET)

        user_action_time = d.pop("userActionTime", UNSET)

        document_uri = d.pop("documentUri", UNSET)

        error = d.pop("error", UNSET)

        activity_id = d.pop("activityId", UNSET)

        inline_suggestion_feedback = cls(
            action=action,
            suggestion_id=suggestion_id,
            latency=latency,
            user_action_time=user_action_time,
            document_uri=document_uri,
            error=error,
            activity_id=activity_id,
        )

        inline_suggestion_feedback.additional_properties = d
        return inline_suggestion_feedback

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
