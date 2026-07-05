class ReprMixin:
    __repr_cols__ = ("id",)

    def __repr__(self) -> str:
        entity_name = self.__class__.__name__
        attrs_str = ", ".join(f"{col}={getattr(self, col)}" for col in self.__repr_cols__)
        return f"{entity_name}({attrs_str})"
