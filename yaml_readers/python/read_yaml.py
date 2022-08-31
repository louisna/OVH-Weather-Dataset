import yaml
import dataclasses


@dataclasses.dataclass
class Link:
    label: str
    load: int


@dataclasses.dataclass
class Router:
    name: str
    peers: dict[str, list["Link"]] = dataclasses.field(default_factory=dict())


def read_yaml(filepath: str) -> dict[str, "Router"]:
    with open(filepath) as fd:
        yaml_data = yaml.full_load(fd)

    all_routers: dict["Router"] = dict()
    for router_name, peers in yaml_data.items():
        router = Router(router_name, dict())
        for peer_data in peers["links"]:
            label = peer_data["label"]
            load = int(peer_data["load"])
            peer_name = peer_data["peer"]
            router.peers.setdefault(peer_name, list()).append(Link(label, load))
        all_routers[router_name] = router
    
    return all_routers


if __name__ == "__main__":
    data = read_yaml("/Users/louisnavarre/Documents/Github/OVH-Analysis/data_september_yaml/weathermap_1630901711.yaml")
    print(data)