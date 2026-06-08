from dataclasses import dataclass

@dataclass(frozen=True, order=True)
class Box:
    a: int
    b: int
    c: int

    def canonical(self):
        return Box(*sorted((self.a, self.b, self.c)))

    def __str__(self):
        return f"{self.a}x{self.b}x{self.c}"


@dataclass
class Catalogue:
    catalogue_name: str
    primes: set[Box]
    searched_no_solution: set[Box]
    row_generators: dict[tuple[int, int], list[int]]
    width_generators: dict[int, list[int]]

    def impossible_reason(self, box: Box) -> str | None:
        return None

    def stats(self):
        print(f"Catalogue: {self.catalogue_name}")
        print(f"Prime boxes: {len(self.primes)}")
        print(f"Row families: {len(self.row_generators)}")
        print(f"Width families: {len(self.width_generators)}")
