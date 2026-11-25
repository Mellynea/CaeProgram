"""Exercise production building-file I/O with real NBT classes, without launching Minecraft."""
from pathlib import Path
import argparse
import json
import os
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build/building-files-check"
JAVA = Path(os.environ.get("JAVA_HOME", "D:/Java/jdk-27")) / "bin"
CACHE = Path.home() / ".gradle/caches"
TARGETS = {"1.20.1": "versions/legacy-1.20.1", "1.21.4": "src/main",
           "1.21.10": "versions/modern-1.21.10"}

STUBS = {
    "net/fabricmc/loader/api/FabricLoader.java": """package net.fabricmc.loader.api;
        public final class FabricLoader {
            private static final FabricLoader INSTANCE = new FabricLoader();
            public static FabricLoader getInstance(){return INSTANCE;}
            public java.nio.file.Path getConfigDir(){return java.nio.file.Path.of(System.getProperty("building.files.check.config"));}
        }""",
    "com/cheatprogram/core/Config.java": """package com.cheatprogram.core;
        public final class Config {
            private static final Object LOCK = new Object();
            public static Object persistenceLock(){return LOCK;}
            public static boolean persistenceAllowed(){return true;}
        }""",
    "com/cheatprogram/util/BuildingProjection.java": """package com.cheatprogram.util;
        public final class BuildingProjection {
            public com.google.gson.JsonObject save(){return new com.google.gson.JsonObject();}
            public static BuildingProjection read(com.google.gson.JsonObject value,int w,int h,int d){return null;}
        }""",
}


def argfile(path, args):
    path.write_text("\n".join('"' + str(arg).replace("\\", "/").replace('"', '\\"') + '"'
                              for arg in args), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prove-baseline", action="store_true",
                        help="Also run HEAD's pre-fix source to demonstrate the reported overflow")
    options = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    dependencies = sorted(p for p in (CACHE / "modules-2/files-2.1").rglob("*.jar")
                          if not p.name.endswith(("-sources.jar", "-javadoc.jar")))
    assert dependencies, "Build dependencies are not cached"
    results = []
    for version, layer in TARGETS.items():
        jars = list((CACHE / "fabric-loom/minecraftMaven/net/minecraft/minecraft-merged").glob(f"{version}-*/*.jar"))
        assert len(jars) == 1, f"Expected one mapped Minecraft {version} JAR, got {jars}"
        target = OUT / version
        stubs = []
        for relative, content in STUBS.items():
            path = target / "stubs" / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            stubs.append(path)
        harness = target / "stubs/BuildingFilesCheck.java"
        source = (ROOT / "verification/java/com/cheatprogram/dev/BuildingFilesCheck.java").read_text("utf-8")
        source = source.replace("/* WRITE_DESTINATION */", "file.toFile()" if version == "1.20.1" else "file")
        harness.write_text(source, encoding="utf-8")
        bridge = ([ROOT / "versions/modern-1.21.10/java/com/cheatprogram/compat/NbtBridge.java"]
                  if version == "1.21.10" else [])
        for baseline in ([True, False] if options.prove_baseline else [False]):
            mode = "baseline" if baseline else "patched"
            production = ROOT / layer / "java/com/cheatprogram/util/BuildingFiles.java"
            if baseline:
                relative = production.relative_to(ROOT).as_posix()
                old_source = subprocess.run(["git", "-C", str(ROOT), "show", f"HEAD:{relative}"],
                                            capture_output=True, check=True).stdout
                production = target / "baseline/com/cheatprogram/util/BuildingFiles.java"
                production.parent.mkdir(parents=True, exist_ok=True)
                production.write_bytes(old_source)
            classes = target / mode
            classes.mkdir(parents=True, exist_ok=True)
            classpath = os.pathsep.join(str(p) for p in [*jars, *dependencies])
            compile_args = target / f"{mode}-compile.args"
            argfile(compile_args, ["-encoding", "UTF-8", "-proc:none", "-cp", classpath, "-d", classes,
                                   *stubs, *bridge, production, harness])
            subprocess.run([str(JAVA / "javac.exe"), "@" + str(compile_args)], check=True)
            config = target / f"{mode}-config"
            runtime_args = target / f"{mode}-run.args"
            argfile(runtime_args, ["-Xmx256m", f"-Dbuilding.files.check.config={config}", "-cp",
                                   os.pathsep.join([str(classes), classpath]),
                                   "BuildingFilesCheck", mode])
            subprocess.run([str(JAVA / "java.exe"), "@" + str(runtime_args)], check=True)
            results.append({"minecraft": version, "mode": mode, "passed": True,
                            "productionSource": str(production), "gameStarted": False})
    (OUT / "results.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    print(f"PASS building-file NBT checks: {len(results)} isolated JVMs")


if __name__ == "__main__":
    main()
