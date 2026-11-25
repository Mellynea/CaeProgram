"""Assemble the shared client and exact Minecraft API layer for NeoForge."""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

def adapt_picture_in_picture(text, mc):
    """NeoForge owns a factory pool per preview state instead of renderer instances."""
    changes = {
        "new GuiEntityRenderer(minecraft.getEntityRenderDispatcher())":
            "new PictureInPictureRendererRegistration<>(GuiEntityRenderState.class, "
            "() -> new GuiEntityRenderer(minecraft.getEntityRenderDispatcher()))",
        "new GuiSkinRenderer()":
            "new PictureInPictureRendererRegistration<>(GuiSkinRenderState.class, GuiSkinRenderer::new)",
        "new GuiBookModelRenderer()":
            "new PictureInPictureRendererRegistration<>(GuiBookModelRenderState.class, GuiBookModelRenderer::new)",
        "new GuiBannerResultRenderer(atlas)":
            "new PictureInPictureRendererRegistration<>(GuiBannerResultRenderState.class, "
            "() -> new GuiBannerResultRenderer(atlas))",
        "new GuiProfilerChartRenderer()":
            "new PictureInPictureRendererRegistration<>(GuiProfilerChartRenderState.class, GuiProfilerChartRenderer::new)",
    }
    if mc == "1.21.10":
        changes = {
            "new GuiEntityRenderer(buffers,minecraft.getEntityRenderDispatcher())":
                "new PictureInPictureRendererRegistration<>(GuiEntityRenderState.class, "
                "pool -> new GuiEntityRenderer(pool, minecraft.getEntityRenderDispatcher()))",
            "new GuiSkinRenderer(buffers)":
                "new PictureInPictureRendererRegistration<>(GuiSkinRenderState.class, GuiSkinRenderer::new)",
            "new GuiBookModelRenderer(buffers)":
                "new PictureInPictureRendererRegistration<>(GuiBookModelRenderState.class, GuiBookModelRenderer::new)",
            "new GuiBannerResultRenderer(buffers,atlas)":
                "new PictureInPictureRendererRegistration<>(GuiBannerResultRenderState.class, "
                "pool -> new GuiBannerResultRenderer(pool, atlas))",
            "new GuiSignRenderer(buffers,atlas)":
                "new PictureInPictureRendererRegistration<>(GuiSignRenderState.class, "
                "pool -> new GuiSignRenderer(pool, atlas))",
            "new GuiProfilerChartRenderer(buffers)":
                "new PictureInPictureRendererRegistration<>(GuiProfilerChartRenderState.class, GuiProfilerChartRenderer::new)",
        }
    for old, new in changes.items():
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    return text.replace(
        "import net.minecraft.client.gui.render.pip.*;",
        "import net.minecraft.client.gui.render.pip.*;\n"
        + ("import net.minecraft.client.gui.render.state.pip.*;\n" if mc == "1.21.10"
           else "import net.minecraft.client.renderer.state.gui.pip.*;\n") +
        "import net.neoforged.neoforge.client.gui.PictureInPictureRendererRegistration;",
    )


def prepare(mc):
    matrix = json.loads((ROOT / "compatibility/neoforge.json").read_text(encoding="utf-8"))
    target = next(item for item in matrix["targets"] if item["minecraft"] == mc)
    output = ROOT / "build/neoforge" / mc / "generated/main"
    layers = [
        ROOT / "src/main",
        *(ROOT / "versions" / name for name in target["sourceLayers"]),
        ROOT / "loaders/neoforge/src/main",
        ROOT / "loaders/neoforge/src" / mc,
    ]
    expected = set()
    for kind in ("java", "resources"):
        files = {}
        for layer in layers:
            for source in (layer / kind).rglob("*"):
                if source.is_file():
                    files[source.relative_to(layer / kind)] = source
        for relative, source in files.items():
            if relative.as_posix() == "fabric.mod.json":
                continue
            # The inherited 1.20.x allocation adapters do not apply to the
            # ByteBufferBuilder API used by all supported NeoForge versions.
            if relative.as_posix() in (
                "com/cheatprogram/compat/legacy/LegacyNativeBuffer.java",
                "com/cheatprogram/mixin/LegacyBufferAccessor.java",
            ):
                continue
            destination = output / kind / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            data = source.read_bytes()
            if relative.suffix == ".java":
                text = data.decode("utf-8").replace(
                    "net.fabricmc.loader.api.FabricLoader", "com.cheatprogram.platform.ModPlatform"
                ).replace("FabricLoader", "ModPlatform")
                if relative.as_posix() == "com/cheatprogram/CheatProgram.java":
                    text = text.replace("import net.fabricmc.api.ClientModInitializer;", "")
                    text = text.replace(" implements ClientModInitializer", "").replace("@Override", "")
                if mc == "1.21.1" and relative.name == "ModPlatform.java":
                    text = text.replace("FMLEnvironment.isProduction()", "FMLEnvironment.production")
                    text = text.replace(
                        "List.copyOf(info.getOwningFile().getFile().getContents().getContentRoots())",
                        "List.of(info.getOwningFile().getFile().findResource(\"\"))",
                    )
                if mc == "1.21.1" and relative.name == "ClickGuiScreen.java":
                    text = text.replace('String version = "1.21.4";',
                        'String version = net.minecraft.SharedConstants.getCurrentVersion().getName();')
                if mc == "1.21.1" and relative.name == "ParticleEffectsEngineMixin.java":
                    text = text.replace("Lnet/minecraft/client/Camera;F)V",
                        "Lnet/minecraft/client/Camera;FLnet/minecraft/client/renderer/culling/Frustum;Ljava/util/function/Predicate;)V")
                    text = text.replace("float partialTick, CallbackInfo ci",
                        "float partialTick, net.minecraft.client.renderer.culling.Frustum frustum, "
                        "java.util.function.Predicate<?> filter, CallbackInfo ci")
                if mc in ("1.21.10", "26.2", "26.3") and relative.name == "GuiBridge.java":
                    text = adapt_picture_in_picture(text, mc)
                if mc in ("1.21.1", "1.21.10") and relative.name == "GameRendererMixin.java":
                    method = "renderWithTooltip" if mc == "1.21.1" else "renderWithTooltipAndSubtitles"
                    old = (f'target="Lnet/minecraft/client/gui/screens/Screen;{method}'
                           '(Lnet/minecraft/client/gui/GuiGraphics;IIF)V"')
                    new = ('remap=false,target="Lnet/neoforged/neoforge/client/ClientHooks;drawScreen('
                           'Lnet/minecraft/client/gui/screens/Screen;Lnet/minecraft/client/gui/GuiGraphics;IIF)V"')
                    assert text.count(old) == 1, old
                    text = text.replace(old, new)
                if mc in ("26.2", "26.3") and relative.name == "NativeGuiScreenOverlayMixin.java":
                    text = text.replace(
                        'target="Lnet/minecraft/client/gui/screens/Screen;extractRenderStateWithTooltipAndSubtitles(',
                        'remap=false,target="Lnet/neoforged/neoforge/client/ClientHooks;extractScreen('
                        'Lnet/minecraft/client/gui/screens/Screen;Ljava/util/Stack;',
                    )
                    text = text.replace(
                        "Screen screen,GuiGraphicsExtractor graphics,",
                        "Screen screen,java.util.Stack<Screen> layers,GuiGraphicsExtractor graphics,",
                    ).replace("original.call(screen,graphics,", "original.call(screen,layers,graphics,")
                if mc == "26.3":
                    from minecraft_relocations import relocate_26_3
                    text = relocate_26_3(text, relative.name)
                data = text.encode("utf-8")
            elif relative.as_posix() == "cheatprogram.mixins.json":
                config = json.loads(data)
                config.pop("refmap", None)
                data = (json.dumps(config, indent=2) + "\n").encode("utf-8")
            if not destination.exists() or destination.read_bytes() != data:
                destination.write_bytes(data)
            expected.add(destination)

    metadata = output / "resources/META-INF/neoforge.mods.toml"
    metadata.parent.mkdir(parents=True, exist_ok=True)
    metadata.write_text(
        f'''modLoader="javafml"
loaderVersion="[{target["fmlMajor"]},)"
license="PolyForm-Noncommercial-1.0.0"
issueTrackerURL="https://github.com/Mellivyne/CaeDuex/issues"
[[mods]]
modId="cheatprogram"
version="{matrix["projectVersion"]}"
displayName="CaeDuex"
displayURL="https://github.com/Mellivyne/CaeDuex"
logoFile="assets/cheatprogram/icon.png"
features={{ javaVersion="[{target["java"]},)" }}
description="In-world application projection, spatial audio, particles, building tools and configurable visual features."
[[mixins]]
config="cheatprogram.mixins.json"
[[dependencies.cheatprogram]]
modId="neoforge"
type="required"
versionRange="[{target["neoforge"]},)"
ordering="NONE"
side="CLIENT"
[[dependencies.cheatprogram]]
modId="minecraft"
type="required"
versionRange="[{mc}]"
ordering="NONE"
side="CLIENT"
''',
        encoding="utf-8",
    )
    expected.add(metadata)
    # Remove obsolete generated files only inside this target's output.
    for path in output.rglob("*"):
        if path.is_file() and path not in expected:
            assert path.resolve().is_relative_to(output.resolve())
            path.unlink()
    print(f"Prepared NeoForge {mc}: {len(expected)} shared and loader files")


if __name__ == "__main__":
    prepare(sys.argv[1])
