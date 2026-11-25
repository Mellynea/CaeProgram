# v1.3fix corrective validation

The starting point is published `main` commit `30a1b1bd9259aa165e944b69e8b4bef32ebd64e2`. The report is [issue #2](https://github.com/Mellynea/CaeProgram/issues/2), describing native-memory exhaustion on Forge 1.20.1. The ZIP attachment was not downloaded or executed; the source investigation used the stack included in the issue text.

## Native allocation lifetime

The real mapped Minecraft `BufferBuilder` and LWJGL allocator were exercised independently for 1.20.1 and 1.20.4, with a 32 MiB allocation budget and no game or window. Each version passed 200,000 normal draws without continuing per-draw allocations, 20,000 empty batches, 20,000 abandoned batches, and 10,000 owned batch creation/disposal cycles. Checks also cover nested batches, completed meshes retained across another draw, close refusal while a mesh is live, retry, idempotence and the unfinished-batch limit. A 16-allocation old-pattern control showed growth and was fully freed.

This caught a second defect during development: empty/abandoned batches retained an internal write offset. Reuse now discards that state only after every outstanding view has been released. Native frees use the same allocator as Minecraft 1.20.1; 1.20.4 uses its public release API. The test agent injects equivalent accessor methods into the actual Minecraft class; it does not launch the full Mixin/game stack. Final Forge reference maps and Fabric's directly remapped accessor fields are checked separately.

## Failure cleanup

Fault injection against the production preview upload methods passed 57 cases across eight API variants, including construction, binding, validation, upload, ownership transfer and cleanup failures. Six shader compilation/link/uniform failure cases passed. Two pre-fix negative controls failed as expected. These checks validate exceptional control flow with test doubles; they are not a full GPU/game rendering test.

## Building file dimensions

`python tools/check_building_files.py` exercises the production file loader/saver with real Minecraft NBT implementations for 1.20.1, 1.21.4 and 1.21.10. Each patched variant passed 2,020 checks: malformed sizes and block counts, mathematical boundaries, 2,000 randomized comparisons and valid save/load and duplicate-name round trips. Separate tests against the starting source demonstrated that dimensions `27905 × 769546 × 859019674` overflowed a Java long to four and were incorrectly accepted; the patch rejects them before multiplication.

## Packaging

Every supported target is built independently: ten Fabric, six Forge and four NeoForge JARs. Packaging checks cover exact game/loader/project metadata, ZIP integrity, module and Mixin presence, project integrity manifests, retained v1.3 functionality and absence of reserved v1.4 3D-projection code. The old-memory accessor is limited to 1.20.x; 1.21.1 retains its existing render-type accessor and API.

All artifacts must share the same source hash before staging. SHA-256 records are listed in `v1.3fix-builds.json` and the release's `SHA256SUMS.txt`. No flashing tests or live gameplay were performed; the reporter's exact machine and third-party mod combinations remain untested.
