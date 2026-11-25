import com.cheatprogram.util.BuildingFiles;
import java.io.IOException;
import java.lang.reflect.InvocationTargetException;
import java.math.BigInteger;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.Random;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.nbt.ListTag;
import net.minecraft.nbt.NbtIo;

/** Uses the shipped BuildingFiles implementation and real compressed NBT, without a game client. */
public final class BuildingFilesCheck {
    private static int checks;

    public static void main(String[] args) throws Exception {
        boolean baseline = args[0].equals("baseline");
        Files.createDirectories(BuildingFiles.directory());
        int[] overflow = {27905, 769546, 859019674};
        require(volume(overflow).equals(BigInteger.ONE.shiftLeft(64).add(BigInteger.valueOf(4))), "Overflow fixture");
        write("overflow", overflow, new int[4]);
        if (baseline) {
            var accepted = BuildingFiles.load("overflow");
            require(accepted.width() == overflow[0] && accepted.count() == 4, "Baseline must demonstrate overflow acceptance");
        } else {
            rejects("overflow");
            int[][] invalid = {{0,1,1}, {-1,1,1}, {1,0,1}, {1,1,0}, {1,1,-1}, {}, {1,1}, {1,1,1,1},
                               {Integer.MAX_VALUE, Integer.MAX_VALUE, Integer.MAX_VALUE}, {BuildingFiles.MAX_BLOCKS,2,1}};
            for (int index = 0; index < invalid.length; index++) {
                write("invalid-" + index, invalid[index], new int[0]);
                rejects("invalid-" + index);
            }
            write("mismatch", new int[]{2,2,2}, new int[7]);
            rejects("mismatch");
            var count = BuildingFiles.class.getDeclaredMethod("checkedBlockCount", int[].class);
            count.setAccessible(true);
            require((int)count.invoke(null, (Object)new int[]{BuildingFiles.MAX_BLOCKS,1,1}) == BuildingFiles.MAX_BLOCKS, "Exact maximum volume");
            require((int)count.invoke(null, (Object)new int[]{1,2,3}) == 6, "Normal count");
            Random random = new Random(1812034);
            for (int index = 0; index < 2000; index++) {
                int[] size = {1 + random.nextInt(Integer.MAX_VALUE - 1), 1 + random.nextInt(100000), 1 + random.nextInt(100000)};
                boolean fits = volume(size).compareTo(BigInteger.valueOf(BuildingFiles.MAX_BLOCKS)) <= 0;
                try {
                    int result = (int)count.invoke(null, (Object)size);
                    require(fits && result == volume(size).intValueExact(), "Bounded volume must equal mathematical volume");
                } catch (InvocationTargetException error) {
                    require(!fits && error.getCause() instanceof IOException, "Oversize must reject as IOException");
                }
            }
        }
        CompoundTag air = new CompoundTag(); air.putString("Name", "minecraft:air");
        int[] blocks = new int[24];
        var saved = BuildingFiles.save(new BuildingFiles.Blueprint("roundtrip", 2, 3, 4, List.of(air), blocks, Map.of()));
        var loaded = BuildingFiles.load(saved.name());
        require(loaded.width() == 2 && loaded.height() == 3 && loaded.depth() == 4, "Roundtrip dimensions");
        require(Arrays.equals(loaded.blocks(), blocks), "Roundtrip block data");
        require(loaded.palette().equals(List.of(air)), "Roundtrip palette");
        var copy = BuildingFiles.save(loaded);
        require(!copy.name().equals(saved.name()), "Existing file preserved on save");
        require(BuildingFiles.load(copy.name()).count() == blocks.length, "Saved copy readable");
        System.out.println("PASS " + args[0] + " building NBT checks: " + checks);
    }

    private static BigInteger volume(int[] size) {
        return BigInteger.valueOf(size[0]).multiply(BigInteger.valueOf(size[1])).multiply(BigInteger.valueOf(size[2]));
    }

    private static void write(String name, int[] size, int[] blocks) throws IOException {
        CompoundTag root = new CompoundTag(); root.putInt("version", 1); root.putString("name", name);
        root.putIntArray("size", size); root.putIntArray("blocks", blocks);
        CompoundTag air = new CompoundTag(); air.putString("Name", "minecraft:air");
        ListTag palette = new ListTag(); palette.add(air); root.put("palette", palette);
        root.put("blockEntities", new ListTag());
        Path file = BuildingFiles.directory().resolve(name + ".cpbuilding");
        NbtIo.writeCompressed(root, /* WRITE_DESTINATION */);
    }

    private static void rejects(String name) throws Exception {
        try { BuildingFiles.load(name); throw new AssertionError("Accepted damaged building: " + name); }
        catch (IOException expected) { checks++; }
    }

    private static void require(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
        checks++;
    }
}
