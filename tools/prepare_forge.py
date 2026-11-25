"""Generate an exact Forge source overlay without changing Fabric source inputs."""
from pathlib import Path
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
mc=sys.argv[1]
matrix=json.loads((ROOT/'compatibility/forge.json').read_text(encoding='utf-8'))
target=next(t for t in matrix['targets'] if t['minecraft']==mc)
output=ROOT/'build/forge'/mc/'generated/main'
layers=[ROOT/'src/main',*[ROOT/'versions'/name for name in target['sourceLayers']],ROOT/'loaders/forge/src/main',ROOT/'loaders/forge/src'/mc]
expected=set()
for kind in ['java','resources']:
    files={}
    for layer in layers:
        for source in (layer/kind).rglob('*'):
            if source.is_file():files[source.relative_to(layer/kind)]=source
    for relative,source in files.items():
        if relative.as_posix()=='fabric.mod.json':continue
        # These adapters access the 1.20.x BufferBuilder allocation, which was
        # replaced by ByteBufferBuilder in 1.21.1 and later.
        if mc not in ('1.20.1','1.20.4') and relative.as_posix() in (
            'com/cheatprogram/compat/legacy/LegacyNativeBuffer.java',
            'com/cheatprogram/mixin/LegacyBufferAccessor.java',
        ):continue
        path=output/kind/relative;path.parent.mkdir(parents=True,exist_ok=True)
        data=source.read_bytes()
        if path.suffix=='.java':
            text=data.decode('utf-8').replace('net.fabricmc.loader.api.FabricLoader','com.cheatprogram.platform.ModPlatform').replace('FabricLoader','ModPlatform')
            if relative.as_posix()=='com/cheatprogram/CheatProgram.java':
                text=text.replace('import net.fabricmc.api.ClientModInitializer;','').replace(' implements ClientModInitializer','').replace('@Override','')
            if mc in ('1.20.1','1.20.4','1.21.1') and relative.as_posix()=='com/cheatprogram/gui/ClickGuiScreen.java':
                import re
                text,count=re.subn(r'String version = "[^"]+";', 'String version = net.minecraft.SharedConstants.getCurrentVersion().getName();',text)
                assert count==1,'Panel version label changed; inspect before packaging'
            if mc != '26.3' and relative.as_posix()=='com/cheatprogram/mixin/GameRendererMixin.java':
                # Forge replaces Screen.renderWithTooltip with its screen-event hook.
                method = 'renderWithTooltipAndSubtitles' if mc in ('1.21.10', '1.21.11') else 'renderWithTooltip'
                old=f'target="Lnet/minecraft/client/gui/screens/Screen;{method}(Lnet/minecraft/client/gui/GuiGraphics;IIF)V"'
                new='target="Lnet/minecraftforge/client/ForgeHooksClient;drawScreen(Lnet/minecraft/client/gui/screens/Screen;Lnet/minecraft/client/gui/GuiGraphics;IIF)V",remap=false'
                assert old in text,'Forge screen render hook changed; inspect the native call before packaging'
                text=text.replace(old,new)
            if mc in ('1.20.1','1.20.4'):
                if relative.as_posix()=='com/cheatprogram/render/R2D.java':
                    # A queued vanilla batch can finish render types and change GL state.
                    # Snapshot the completed batch, not the state preceding that flush.
                    text=text.replace('\r\n','\n')
                    old='LegacyRenderSystem.captureModelView();\n\t\tframeState = new RenderStateSnapshot();\n\t\ttry {\n\t\t\tgraphics = g;\n\t\t\tg.flush();'
                    new='g.flush();\n\t\tLegacyRenderSystem.captureModelView();\n\t\tframeState = new RenderStateSnapshot();\n\t\ttry {\n\t\t\tgraphics = g;'
                    assert text.count(old)==1,'Legacy R2D entry changed; inspect its batch boundary'
                    text=text.replace(old,new)
                    old='com.cheatprogram.compat.legacy.LegacyRenderSystem.drawWithShader('
                    assert text.count(old)>=3,'Legacy UI draw routes changed'
                    text=text.replace(old,'com.cheatprogram.forge.LegacyBlendState.standard();'+old)
                if relative.as_posix()=='com/cheatprogram/render/RenderStateSnapshot.java':
                    old='LegacyRenderSystem.blendFuncSeparate(srcRgb, dstRgb, srcAlpha, dstAlpha);'
                    assert text.count(old)==1
                    text=text.replace(old,'com.cheatprogram.forge.LegacyBlendState.factors(srcRgb, dstRgb, srcAlpha, dstAlpha);')
                    old='final ShaderInstance shader = LegacyRenderSystem.getShader();'
                    assert text.count(old)==1
                    text=text.replace(old,old+'\n        final com.mojang.blaze3d.shaders.BlendMode nativeBlendMode=com.cheatprogram.forge.LegacyBlendState.capture();')
                    old='GlStateManager._glUseProgram(program);'
                    assert text.count(old)==1
                    text=text.replace(old,old+'com.cheatprogram.forge.LegacyBlendState.restore(nativeBlendMode);')
                if relative.as_posix()=='com/cheatprogram/render/Backdrop.java':
                    old='LegacyRenderSystem.setShader(shader);\n\t\tshader.setSampler("InSampler", texture);'
                    text=text.replace('\r\n','\n')
                    assert text.count(old)==1
                    text=text.replace(old,'if(program==Shaders.BACKDROP){LegacyRenderSystem.enableBlend();com.cheatprogram.forge.LegacyBlendState.standard();}\n\t\t'+old)
                if relative.as_posix()=='com/cheatprogram/mixin/KeyboardHandlerMixin.java':
                    # Forge events and the window poll share an edge detector for the panel shortcut.
                    text=text.replace('com.cheatprogram.gui.PanelShortcut.handle(key, action)',
                                      'com.cheatprogram.forge.ForgeClientEvents.panelKey(key, action)')
                native_events={
                    'com/cheatprogram/mixin/MinecraftMixin.java':[
                        'com.cheatprogram.util.ImeSupport.tick();','ModuleManager.onTick();','DevTools.tick();','ModuleManager.onPostTick();'],
                    'com/cheatprogram/mixin/KeyboardHandlerMixin.java':['ModuleManager.onInput(key, action);'],
                    'com/cheatprogram/mixin/MouseHandlerMixin.java':['if (button > 1) ModuleManager.onInput(KeyNames.MOUSE_OFFSET + button, action);'],
                    'com/cheatprogram/mixin/GuiMixin.java':['HudRenderer.render(graphics, delta);'],
                }
                for call in native_events.get(relative.as_posix(),[]):
                    assert text.count(call)==1,(relative,call)
                    text=text.replace(call,'/* Dispatched once through ForgeClientEvents. */')
            if mc == '26.3':
                from minecraft_relocations import relocate_26_3
                text = relocate_26_3(text, path.name)
                if relative.name == 'ModPlatform.java':
                    text = text.replace('ModList.get().', 'ModList.')
            if mc == '1.21.1' and relative.name == 'ParticleEffectsEngineMixin.java':
                text = text.replace('Lnet/minecraft/client/Camera;F)V',
                        'Lnet/minecraft/client/Camera;FLnet/minecraft/client/renderer/culling/Frustum;)V')
                text = text.replace('float partialTick, CallbackInfo ci',
                        'float partialTick, net.minecraft.client.renderer.culling.Frustum frustum, CallbackInfo ci')
            data=text.encode('utf-8')
        elif relative.as_posix()=='cheatprogram.mixins.json':
            config=json.loads(data)
            if mc == '26.3':
                # Forge's Mixin 0.8.7 declares Java levels through 21.
                config['compatibilityLevel']='JAVA_21'
                config['client'].remove('NativeGuiScreenOverlayMixin')
            if mc in ('1.20.1','1.20.4'):
                config['refmap']='cheatprogram.refmap.json';config['compatibilityLevel']='JAVA_17'
                config['client'].append('LegacyBlendModeAccessor')
            data=(json.dumps(config,indent=2)+'\n').encode('utf-8')
        if not path.exists() or path.read_bytes()!=data:path.write_bytes(data)
        expected.add(path)
metadata=output/'resources/META-INF/mods.toml';metadata.parent.mkdir(parents=True,exist_ok=True)
major=int(target['forge'].split('.')[0])
metadata.write_text(f'''modLoader="javafml"
loaderVersion="[{major},)"
license="PolyForm-Noncommercial-1.0.0"
issueTrackerURL="https://github.com/Mellivyne/CaeDuex/issues"
clientSideOnly=true
[[mods]]
modId="cheatprogram"
version="{matrix['projectVersion']}"
displayName="CaeDuex"
displayURL="https://github.com/Mellivyne/CaeDuex"
logoFile="assets/cheatprogram/icon.png"
displayTest="IGNORE_ALL_VERSION"
features={{ java_version="[{target['java']},)" }}
description="In-world application projection, spatial audio, particles, building tools and configurable visual features."
[[dependencies.cheatprogram]]
modId="forge"
mandatory=true
versionRange="[{target['forge']},{major+1})"
ordering="NONE"
side="CLIENT"
[[dependencies.cheatprogram]]
modId="minecraft"
mandatory=true
versionRange="[{mc}]"
ordering="NONE"
side="CLIENT"
''',encoding='utf-8')
expected.add(metadata)
pack=output/'resources/pack.mcmeta'
pack_format=target.get('packFormat')
if pack_format is not None:
    formats = {'min_format': pack_format, 'max_format': pack_format} if isinstance(pack_format,list) else {'pack_format':pack_format}
    pack.write_text(json.dumps({'pack':{'description':f"CaeDuex v{matrix['projectVersion']} resources",
        **formats}},indent=2)+'\n',encoding='utf-8')
    expected.add(pack)
if mc in ('1.20.1','1.20.4','1.21.1'):
    nested=output/'resources/META-INF/jarjar/metadata.json';nested.parent.mkdir(parents=True,exist_ok=True)
    nested.write_text(json.dumps({'jars':[{'identifier':{'group':'io.github.llamalad7','artifact':'mixinextras-forge'},'version':{'range':'[0.5.0,)','artifactVersion':'0.5.0'},'path':'META-INF/jarjar/mixinextras-forge-0.5.0.jar'}]},indent=2)+'\n',encoding='utf-8')
    expected.add(nested)
for old in output.rglob('*'):
    if old.is_file() and old not in expected:
        assert old.resolve().is_relative_to(output.resolve())
        old.unlink()
assert not any('net.fabricmc' in p.read_text(encoding='utf-8') for p in (output/'java').rglob('*.java') if p.name!='PersonalReports.java')
print(f'Prepared Forge {mc}: {len(expected)} source/resource files')
