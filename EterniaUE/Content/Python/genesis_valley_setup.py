"""Automation helpers for Epic B (Genesis Valley environment).

Run inside the Unreal Editor's Python console or via the Python Editor Script Plugin.
The script ensures the Genesis Valley level contains baseline atmosphere, lighting,
and post-process configuration matching docs/tasks.md items B.1 and B.2.
"""

import unreal

LEVEL_PACKAGE_PATH = "/Game/GenesisValley"
LEVEL_NAME = "GenesisValley"
LEVEL_ASSET_PATH = f"{LEVEL_PACKAGE_PATH}/{LEVEL_NAME}"


def log(message: str) -> None:
    unreal.log(f"[GenesisValleySetup] {message}")


def warn(message: str) -> None:
    unreal.log_warning(f"[GenesisValleySetup] {message}")


def safe_set(obj, prop: str, value) -> None:
    try:
        obj.set_editor_property(prop, value)
    except Exception as exc:  # noqa: BLE001 - UE raises generic Exceptions here
        warn(f"Unable to set {prop}: {exc}")


def ensure_level_loaded() -> unreal.World:
    """Create the Genesis Valley level on first run and load it."""
    asset_lib = unreal.EditorAssetLibrary
    level_lib = unreal.EditorLevelLibrary

    if not asset_lib.does_directory_exist(LEVEL_PACKAGE_PATH):
        asset_lib.make_directory(LEVEL_PACKAGE_PATH)
        log(f"Created content folder {LEVEL_PACKAGE_PATH}")

    if not asset_lib.does_asset_exist(LEVEL_ASSET_PATH):
        log("Level not found; generating a fresh Genesis Valley level")
        level_lib.new_level(LEVEL_ASSET_PATH)
    else:
        level_lib.load_level(LEVEL_ASSET_PATH)
        log("Loaded existing Genesis Valley level")

    return level_lib.get_editor_world()


def find_actor(label: str):
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == label:
            return actor
    return None


def get_or_spawn(label: str, actor_class, location=unreal.Vector(0.0, 0.0, 0.0),
                 rotation=unreal.Rotator(0.0, 0.0, 0.0)):
    actor = find_actor(label)
    if actor:
        return actor
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class, location, rotation)
    actor.set_actor_label(label)
    return actor


def configure_directional_light() -> None:
    light = get_or_spawn(
        label="GV_SunLight",
        actor_class=unreal.DirectionalLight,
        location=unreal.Vector(-2000.0, -5000.0, 6000.0),
        rotation=unreal.Rotator(-35.0, 45.0, 0.0),
    )
    component = light.get_component_by_class(unreal.DirectionalLightComponent)
    safe_set(component, "mobility", unreal.ComponentMobility.MOVABLE)
    safe_set(component, "intensity", 80000.0)  # lux (~mid-day sun)
    safe_set(component, "b_use_temperature", True)
    safe_set(component, "temperature", 5200.0)
    safe_set(component, "b_enable_light_shaft_bloom", True)
    safe_set(component, "light_shaft_blend_radius", 1.5)
    safe_set(component, "light_shaft_bloom", 0.6)
    safe_set(component, "b_cast_dynamic_shadow", True)
    safe_set(component, "dynamic_shadow_distance_movable_light", 20000.0)
    log("Configured movable directional light with warm sun coloration")


def configure_sky_light() -> None:
    sky_light = get_or_spawn(
        label="GV_SkyLight",
        actor_class=unreal.SkyLight,
        location=unreal.Vector(0.0, 0.0, 0.0),
    )
    component = sky_light.get_component_by_class(unreal.SkyLightComponent)
    safe_set(component, "mobility", unreal.ComponentMobility.MOVABLE)
    safe_set(component, "b_real_time_capture", True)
    safe_set(component, "intensity", 0.9)
    safe_set(sky_light, "b_enabled", True)
    log("Configured real-time capture skylight")


def configure_sky_atmosphere() -> None:
    sky_atmosphere = get_or_spawn(
        label="GV_SkyAtmosphere",
        actor_class=unreal.SkyAtmosphere,
        location=unreal.Vector(0.0, 0.0, 0.0),
    )
    log("Ensured SkyAtmosphere actor exists")


def configure_height_fog() -> None:
    fog = get_or_spawn(
        label="GV_ExponentialHeightFog",
        actor_class=unreal.ExponentialHeightFog,
        location=unreal.Vector(0.0, 0.0, 0.0),
    )
    component = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
    safe_set(component, "volumetric_fog", True)
    safe_set(component, "fog_density", 0.008)
    safe_set(component, "fog_height_falloff", 0.2)
    safe_set(component, "volumetric_scattering_distribution", 0.15)
    safe_set(component, "volumetric_fog_scattering_distribution", 0.2)
    safe_set(component, "volumetric_fog_extinction_scale", 1.15)
    safe_set(component, "volumetric_fog_albedo", unreal.LinearColor(0.92, 0.85, 0.76, 1.0))
    log("Enabled volumetric height fog")


def configure_post_process_volume() -> None:
    volume = get_or_spawn(
        label="GV_PostProcess",
        actor_class=unreal.PostProcessVolume,
        location=unreal.Vector(0.0, 0.0, 0.0),
    )
    safe_set(volume, "b_unbound", True)
    safe_set(volume, "priority", 1.0)

    settings = volume.get_editor_property("settings")
    safe_set(settings, "b_override_bloom_intensity", True)
    safe_set(settings, "bloom_intensity", 0.8)
    safe_set(settings, "b_override_bloom_threshold", True)
    safe_set(settings, "bloom_threshold", -1.0)

    safe_set(settings, "b_override_color_saturation", True)
    safe_set(settings, "color_saturation", unreal.Vector4(0.9, 1.05, 1.1, 1.0))
    safe_set(settings, "b_override_color_contrast", True)
    safe_set(settings, "color_contrast", unreal.Vector4(1.05, 0.98, 0.96, 1.0))

    safe_set(settings, "b_override_scene_fringing_intensity", True)
    safe_set(settings, "scene_fringing_intensity", 0.2)

    safe_set(settings, "b_override_light_shaft_bloom_intensity", True)
    safe_set(settings, "light_shaft_bloom_intensity", 0.4)

    safe_set(volume, "settings", settings)
    log("Configured unbound post-process volume with warm grading and subtle effects")


def main():
    ensure_level_loaded()
    configure_sky_atmosphere()
    configure_directional_light()
    configure_sky_light()
    configure_height_fog()
    configure_post_process_volume()
    unreal.EditorLevelLibrary.save_current_level()
    log("Genesis Valley baseline lighting setup complete")


if __name__ == "__main__":
    main()
