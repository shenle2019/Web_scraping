import com.github.unidbg.AndroidEmulator;
import com.github.unidbg.Module;
import com.github.unidbg.linux.android.AndroidEmulatorBuilder;
import com.github.unidbg.linux.android.AndroidResolver;
import com.github.unidbg.linux.android.dvm.AbstractJni;
import com.github.unidbg.linux.android.dvm.BaseVM;
import com.github.unidbg.linux.android.dvm.DalvikModule;
import com.github.unidbg.linux.android.dvm.DvmClass;
import com.github.unidbg.linux.android.dvm.DvmObject;
import com.github.unidbg.linux.android.dvm.StringObject;
import com.github.unidbg.linux.android.dvm.VM;
import com.github.unidbg.linux.android.dvm.VaList;
import com.github.unidbg.memory.Memory;

import java.io.File;

/**
 * 仅限学习研究，禁止商用。
 *
 * 小红书 libshield.so（32 位）—— unidbg 只跑初始化链：
 *   static { initializeNative(); }  ->  native void initializeNative()
 *   构造器 XhsHttpInterceptor(String) -> native long initialize(String)
 *
 * intercept(Interceptor.Chain, long) 需要完整 okhttp3 环境（Request/Response/Headers），
 * 属于 day29 大量补环境的部分，本 demo 不伪造这部分结果。
 */
public class XhsShieldDemo extends AbstractJni {

    /** 第一层补环境：JNI_OnLoad 里 so 会取 Application.getPackageName()。 */
    @Override
    public DvmObject<?> callObjectMethodV(BaseVM vm, DvmObject<?> dvmObject, String signature, VaList vaList) {
        if ("android/app/Application->getPackageName()Ljava/lang/String;".equals(signature)) {
            return new StringObject(vm, "com.xingin.xhs");
        }
        System.out.println("[env] 未处理的对象方法: " + signature);
        return super.callObjectMethodV(vm, dvmObject, signature, vaList);
    }

    public static void main(String[] args) throws Exception {
        AndroidEmulator emulator = AndroidEmulatorBuilder.for32Bit()
                .setProcessName("com.xingin.xhs")
                .build();
        Memory memory = emulator.getMemory();
        memory.setLibraryResolver(new AndroidResolver(23));

        VM vm = emulator.createDalvikVM();
        vm.setJni(new XhsShieldDemo());

        DalvikModule dm = vm.loadLibrary(new File("apks/xhs/libshield.so"), false);
        Module module = dm.getModule();
        System.out.println("[xhs] so base = 0x" + Long.toHexString(module.base));
        dm.callJNI_OnLoad(emulator);

        DvmClass interceptor = vm.resolveClass("com/xingin/shield/http/XhsHttpInterceptor");
        interceptor.callStaticJniMethod(emulator, "initializeNative()V");
        System.out.println("[xhs] initializeNative() ok");

        com.github.unidbg.linux.android.dvm.DvmObject<?> ret = interceptor.callStaticJniMethodObject(
                emulator, "initialize(Ljava/lang/String;)J",
                new com.github.unidbg.linux.android.dvm.StringObject(vm, "{}"));
        Object value = ret.getValue();
        long cPtr = value instanceof Number ? ((Number) value).longValue() : -1L;
        System.out.println("[xhs] initialize(\"{}\") = " + cPtr);
        emulator.close();
    }
}
