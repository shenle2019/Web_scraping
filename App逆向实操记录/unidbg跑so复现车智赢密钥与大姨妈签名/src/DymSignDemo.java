import com.github.unidbg.AndroidEmulator;
import com.github.unidbg.Module;
import com.github.unidbg.linux.android.AndroidEmulatorBuilder;
import com.github.unidbg.linux.android.AndroidResolver;
import com.github.unidbg.linux.android.dvm.AbstractJni;
import com.github.unidbg.linux.android.dvm.DalvikModule;
import com.github.unidbg.linux.android.dvm.DvmClass;
import com.github.unidbg.linux.android.dvm.StringObject;
import com.github.unidbg.linux.android.dvm.VM;
import com.github.unidbg.memory.Memory;

import java.io.File;

/**
 * 仅限学习研究，禁止商用。
 *
 * 大姨妈 libCrypt.so（64 位）—— unidbg 调用 encrypt_data(0, 明文, 明文长度)。
 * 明文取自 day22 的 frida 实测入参，签名结果已有 frida 真值可比对。
 */
public class DymSignDemo extends AbstractJni {

    private static final String PLAIN =
            "885105cf0494dd2301b70faf94b0b39d41540e55user/login18953675221WA89qByLlDeaGjmVNzXm/w==";

    public static void main(String[] args) throws Exception {
        AndroidEmulator emulator = AndroidEmulatorBuilder.for64Bit()
                .setProcessName("com.yoloho.dayima")
                .build();
        Memory memory = emulator.getMemory();
        memory.setLibraryResolver(new AndroidResolver(23));

        VM vm = emulator.createDalvikVM();
        vm.setJni(new DymSignDemo());

        DalvikModule dm = vm.loadLibrary(new File("apks/dym/libCrypt.so"), false);
        Module module = dm.getModule();
        System.out.println("[unidbg] so base = 0x" + Long.toHexString(module.base));
        dm.callJNI_OnLoad(emulator);

        DvmClass crypt = vm.resolveClass("com/yoloho/libcore/util/Crypt");
        StringObject sign = crypt.callStaticJniMethodObject(
                emulator,
                "encrypt_data(JLjava/lang/String;J)Ljava/lang/String;",
                0,
                new StringObject(vm, PLAIN),
                PLAIN.length());
        System.out.println("[unidbg] plain length = " + PLAIN.length());
        System.out.println("[unidbg] sign = " + sign.getValue());
        emulator.close();
    }
}
