from pydantic import BaseModel


class BaseModelDataStructure(BaseModel):
    def __iter__(self):
        return iter(self.__root__)

    def __getitem__(self, item):
        return self.__root__[item]

    def __setitem__(self, key, value):
        self.__root__[key] = value

    def __getattr__(self, name):
        return getattr(self.__root__, name)

    def __iadd__(self, other: "BaseModelDataStructure"):
        self.__root__ += other.__root__
        return self

    def __ior__(self, other: "BaseModelDataStructure"):
        self.__root__ |= other.__root__
        return self

    def __len__(self):
        return len(self.__root__)
