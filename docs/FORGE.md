# Forge builds

CaeDuex v1.3fix has separate Forge client artifacts.

| Minecraft | Forge build used | Required Java | Artifact |
| --- | --- | --- | --- |
| 1.20.1 | 47.4.0 | 21 or newer | `caeduex-v1.3fix-forge-mc1.20.1.jar` |
| 1.20.4 | 49.2.13 | 21 or newer | `caeduex-v1.3fix-forge-mc1.20.4.jar` |
| 1.21.1 | 52.1.21 | 21 or newer | `caeduex-v1.3fix-forge-mc1.21.1.jar` |
| 1.21.10 | 60.1.18 | 21 or newer | `caeduex-v1.3fix-forge-mc1.21.10.jar` |
| 1.21.11 | 61.2.5 | 21 or newer | `caeduex-v1.3fix-forge-mc1.21.11.jar` |
| 26.3 | 66.1.5 | 25 or newer | `caeduex-v1.3fix-forge-mc26.3.jar` |

The Forge dependency ranges stay within their respective loader major versions. Use the matching loader and Minecraft version, and install one CaeDuex JAR in the instance's `mods` folder. Configuration remains local under `config/cheatprogram-open/`.

## Build

Use Python 3 and a Java 25 Gradle runtime to build all targets.

```powershell
python tools/build_forge.py
```

To build one target, append its Minecraft version. The script uses ForgeGradle 6 for the 1.20 builds and ForgeGradle 7 for the newer builds. It generates the matching source and resource overlay, then seals and verifies the packaged JAR. The JARs and SHA-256 checksums are in `outputs/forge/`.

The 1.20 targets compile legacy mixins for Java 17, reobfuscate to SRG, and include a generated mixin reference map. MixinExtras Forge 0.5.0 is bundled through Jar-in-Jar discovery on 1.20.1, 1.20.4, and 1.21.1. The local ZXing QR encoder is included in all Forge artifacts.

Loader path and metadata calls use a Forge adapter. Fabric classes and `fabric.mod.json` are absent from the Forge JARs. The Forge client setup event initializes the same declared feature set through the shared client entry code.

## Verification

Packaging checks validate exact Minecraft and Java requirements, the declared module scope, loader entry, mixins, and installed-resource integrity records.

`ForgeMixinSurfaceCheck` checks selectors and explicit invocation/field targets against each actual mapped Forge Minecraft JAR without starting Minecraft. Missing optional `@Pseudo` companion targets are counted separately. This checks names and descriptors; it does not execute mixins, validate every injector ordinal, render a frame or test interaction with other mods.

The new Forge targets were launched in isolated client instances to check mod initialization and startup rendering. See the [artifact manifest](../outputs/forge/manifest.json) for the per-target verification status.

The build structure follows the [official Forge MDK](https://github.com/MinecraftForge/MinecraftForge/tree/1.20.4/mdk), [Forge mod metadata](https://docs.minecraftforge.net/en/1.20.1/gettingstarted/modfiles/) and [MixinGradle documentation](https://github.com/SpongePowered/MixinGradle).
