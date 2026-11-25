package com.cheatprogram.compat.legacy;

import com.mojang.blaze3d.vertex.BufferBuilder;
import com.cheatprogram.mixin.LegacyBufferAccessor;
import org.lwjgl.system.MemoryUtil;

final class LegacyNativeBuffer {
    private LegacyNativeBuffer() {}
    static boolean available(BufferBuilder buffer) {
        var access = (LegacyBufferAccessor)(Object)buffer;
        return !buffer.building() && access.cheatprogram$renderedBufferCount() == 0 && access.cheatprogram$buffer() != null;
    }
    static void prepareReuse(BufferBuilder buffer) {
        if (!available(buffer)) throw new IllegalStateException("Buffer is not available");
        // An empty/abandoned batch can leave nextElementByte advanced even
        // after endOrDiscardIfEmpty resets building. No views remain here.
        buffer.discard();
        ((LegacyBufferAccessor)(Object)buffer).cheatprogram$buffer().clear();
    }
    static void ensureNoRenderedBuffers(BufferBuilder buffer) {
        if (((LegacyBufferAccessor)(Object)buffer).cheatprogram$renderedBufferCount() != 0)
            throw new IllegalStateException("Buffer still in use");
    }
    static void abandon(BufferBuilder buffer) {
        if (buffer.building()) {
            var mesh = buffer.endOrDiscardIfEmpty();
            if (mesh != null) mesh.release();
        }
    }
    static void release(BufferBuilder buffer) {
        var access = (LegacyBufferAccessor)(Object)buffer;
        if (access.cheatprogram$buffer() == null) return;
        ensureNoRenderedBuffers(buffer);
        if (buffer.building()) throw new IllegalStateException("Buffer still building");
        // MemoryTracker.create uses this same native allocator in Minecraft 1.20.1.
        MemoryUtil.getAllocator(false).free(MemoryUtil.memAddress0(access.cheatprogram$buffer()));
        access.cheatprogram$buffer(null);
    }
}
