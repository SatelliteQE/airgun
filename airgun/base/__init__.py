def load_application_collections():
    from pkg_resources import iter_entry_points

    return {
        ep.name: ep.resolve() for ep in iter_entry_points("airgun.application_collections")
    }
