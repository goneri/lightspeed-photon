from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar
from typing import Union

import attr

from ..models.trigger_enum import TriggerEnum
from ..types import UNSET
from ..types import Unset

T = TypeVar("T", bound="AnsibleContentFeedback")


@attr.s(auto_attribs=True)
class AnsibleContentFeedback:
    """
    Attributes:
        content (str): Ansible file content.
        document_uri (str):
        trigger (TriggerEnum):
        activity_id (Union[Unset, str]): A UUID that identifies a user activity session to the document uploaded.
    """

    content: str
    document_uri: str
    trigger: TriggerEnum
    activity_id: Union[Unset, str] = UNSET
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        content = self.content
        document_uri = self.document_uri
        trigger = self.trigger.value

        activity_id = self.activity_id

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "content": content,
                "documentUri": document_uri,
                "trigger": trigger,
            }
        )
        if activity_id is not UNSET:
            field_dict["activityId"] = activity_id

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        content = d.pop("content")

        document_uri = d.pop("documentUri")

        trigger = TriggerEnum(d.pop("trigger"))

        activity_id = d.pop("activityId", UNSET)

        ansible_content_feedback = cls(
            content=content,
            document_uri=document_uri,
            trigger=trigger,
            activity_id=activity_id,
        )

        ansible_content_feedback.additional_properties = d
        return ansible_content_feedback

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
