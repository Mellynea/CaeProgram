package com.cheatprogram.compat.legacy;
import com.mojang.blaze3d.vertex.VertexFormat;
public final class LegacyTesselator {
    private static final LegacyTesselator INSTANCE=new LegacyTesselator();
    private final java.util.List<LegacyBufferBuilder> buffers=new java.util.ArrayList<>();
    private static final int MAX_UNFINISHED_BATCHES=32;
    public static LegacyTesselator getInstance(){return INSTANCE;}
    public LegacyBufferBuilder begin(VertexFormat.Mode mode,VertexFormat format){
        for(var buffer:buffers) if(LegacyNativeBuffer.available(buffer)) {LegacyNativeBuffer.prepareReuse(buffer);buffer.begin(mode,format);return buffer;}
        // A forgotten/failed batch must not cause an unlimited chain of native allocations.
        if(buffers.size()>=MAX_UNFINISHED_BATCHES) throw new IllegalStateException("Too many unfinished render batches");
        var buffer=new LegacyBufferBuilder(32768,mode,format);buffers.add(buffer);return buffer;
    }
}
