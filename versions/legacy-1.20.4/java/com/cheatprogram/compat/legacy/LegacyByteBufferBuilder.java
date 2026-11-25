package com.cheatprogram.compat.legacy;

/** Owns the separate native allocations used by the old renderer's builders. */
public final class LegacyByteBufferBuilder extends com.mojang.blaze3d.vertex.BufferBuilder implements AutoCloseable {
    final int capacity;
    private final java.util.List<LegacyBufferBuilder> owned = new java.util.ArrayList<>();
    private boolean closed;

    public LegacyByteBufferBuilder(int capacity) { super(capacity); this.capacity = capacity; }
    int openCapacity() {
        if (closed) throw new IllegalStateException("Memory already closed");
        return capacity;
    }
    void own(LegacyBufferBuilder buffer) {
        if (closed) throw new IllegalStateException("Memory already closed");
        owned.add(buffer);
    }
    @Override public void close() {
        if (closed) return;
        // Do not partially dispose a batch while any uploaded view still refers to it.
        LegacyNativeBuffer.ensureNoRenderedBuffers(this);
        for (var buffer : owned) LegacyNativeBuffer.ensureNoRenderedBuffers(buffer);
        for (var buffer : owned) buffer.abandon();
        LegacyNativeBuffer.abandon(this);
        // A failed close remains retryable; already released allocations are harmless.
        for (var buffer : owned) LegacyNativeBuffer.release(buffer);
        LegacyNativeBuffer.release(this);
        owned.clear();
        closed = true;
    }
}
