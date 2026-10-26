import com.github.unidbg.AndroidEmulator;
import com.github.unidbg.Module;
import com.github.unidbg.linux.android.AndroidEmulatorBuilder;
import com.github.unidbg.linux.android.AndroidResolver;
import com.github.unidbg.linux.android.dvm.AbstractJni;
import com.github.unidbg.linux.android.dvm.DalvikModule;
import com.github.unidbg.linux.android.dvm.DvmClass;
import com.github.unidbg.linux.android.dvm.DvmObject;
import com.github.unidbg.linux.android.dvm.StringObject;
import com.github.unidbg.linux.android.dvm.VM;
import com.github.unidbg.memory.Memory;

import java.io.File;

/**
 * 仅限学习研究，禁止商用。
 *
 * 车智赢 libnative-lib.so（静态注册）—— 用 unidbg 在 PC 上直接跑 JNI。
 * 目标：调用 com.autohome.ahkit.jni.CheckSignUtil.get3desKey(Context) 拿到 3DES 密钥。
 */
public class CheSignDemo extends AbstractJni {

    public static void main(String[] args) throws Exception {
        AndroidEmulator emulator = AndroidEmulatorBuilder.for32Bit()
                .setProcessName("com.che168.autotradercloud")
                .build();
        Memory memory = emulator.getMemory();
        memory.setLibraryResolver(new AndroidResolver(23));

        VM vm = emulator.createDalvikVM(new File("apks/che/che3.32.1.apk"));
        vm.setJni(new CheSignDemo());

        DalvikModule dm = vm.loadLibrary(new File("apks/che/libnative-lib.so"), false);
        Module module = dm.getModule();
        System.out.println("[unidbg] so base = 0x" + Long.toHexString(module.base));
        dm.callJNI_OnLoad(emulator);

        DvmClass clazz = vm.resolveClass("com/autohome/ahkit/jni/CheckSignUtil");
        DvmObject<?> context = vm.resolveClass("android/content/Context").newObject(null);
        StringObject key = clazz.callStaticJniMethodObject(
                emulator,
                "get3desKey(Landroid/content/Context;)Ljava/lang/String;",
                context);
        System.out.println("[unidbg] get3desKey = " + key.getValue());
        System.out.println("[unidbg] key length = " + key.getValue().length());
        emulator.close();
    }
}
