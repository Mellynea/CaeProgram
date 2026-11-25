package com.cheatprogram.mixin;

import com.mojang.blaze3d.vertex.BufferBuilder;
import java.nio.ByteBuffer;
import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.gen.Accessor;

@Mixin(BufferBuilder.class)
public interface LegacyBufferAccessor {
    @Accessor("buffer") ByteBuffer cheatprogram$buffer();
    @Accessor("buffer") void cheatprogram$buffer(ByteBuffer buffer);
    @Accessor("renderedBufferCount") int cheatprogram$renderedBufferCount();
}
