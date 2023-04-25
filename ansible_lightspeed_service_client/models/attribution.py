from typing import Any
from typing import Dict
from typing import List
from typing import Type
from typing import TypeVar

import attr

T = TypeVar("T", bound="Attribution")


@attr.s(auto_attribs=True)
class Attribution:
    """
    Attributes:
        repo_name (str):
        repo_url (str):
        path (str):
        license_ (str):
        data_source (str):
        ansible_type (str):
        score (float):
    """

    repo_name: str
    repo_url: str
    path: str
    license_: str
    data_source: str
    ansible_type: str
    score: float
    additional_properties: Dict[str, Any] = attr.ib(init=False, factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        repo_name = self.repo_name
        repo_url = self.repo_url
        path = self.path
        license_ = self.license_
        data_source = self.data_source
        ansible_type = self.ansible_type
        score = self.score

        field_dict: Dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repo_name": repo_name,
                "repo_url": repo_url,
                "path": path,
                "license": license_,
                "data_source": data_source,
                "ansible_type": ansible_type,
                "score": score,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: Type[T], src_dict: Dict[str, Any]) -> T:
        d = src_dict.copy()
        repo_name = d.pop("repo_name")

        repo_url = d.pop("repo_url")

        path = d.pop("path")

        license_ = d.pop("license")

        data_source = d.pop("data_source")

        ansible_type = d.pop("ansible_type")

        score = d.pop("score")

        attribution = cls(
            repo_name=repo_name,
            repo_url=repo_url,
            path=path,
            license_=license_,
            data_source=data_source,
            ansible_type=ansible_type,
            score=score,
        )

        attribution.additional_properties = d
        return attribution

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
