/*
 * 复刻课件 4.x 节里"安全团队写的检测 so"。
 *
 * 只做一件事：扫描当前进程有没有被 Frida 注入。
 *   - /proc/self/maps 里出现 frida / gum-js-loop / linjector 等特征
 *   - /proc/self/task/<tid>/comm 里出现 gum-js-loop / gmain / pool-frida 等线程名
 *
 * 命中返回 JNI_TRUE，由 Java 层杀进程。
 * 本 so 与业务完全无关，删掉之后 App 依然可以正常跑（Java 层捕获 UnsatisfiedLinkError）。
 */
#include <jni.h>
#include <dirent.h>
#include <stdio.h>
#include <string.h>
#include <unistd.h>

static int scan_maps(void) {
    FILE *fp = fopen("/proc/self/maps", "r");
    if (fp == NULL) {
        return 0;
    }
    char line[1024];
    int hit = 0;
    while (fgets(line, sizeof(line), fp) != NULL) {
        if (strstr(line, "frida") != NULL ||
            strstr(line, "gum-js-loop") != NULL ||
            strstr(line, "linjector") != NULL ||
            strstr(line, "gadget") != NULL) {
            hit = 1;
            break;
        }
    }
    fclose(fp);
    return hit;
}

static int scan_threads(void) {
    DIR *dir = opendir("/proc/self/task");
    if (dir == NULL) {
        return 0;
    }
    int hit = 0;
    struct dirent *entry;
    while ((entry = readdir(dir)) != NULL) {
        if (entry->d_name[0] == '.') {
            continue;
        }
        char path[256];
        snprintf(path, sizeof(path), "/proc/self/task/%s/comm", entry->d_name);
        FILE *fp = fopen(path, "r");
        if (fp == NULL) {
            continue;
        }
        char comm[64] = {0};
        if (fgets(comm, sizeof(comm), fp) != NULL) {
            if (strstr(comm, "gum-js-loop") != NULL ||
                strstr(comm, "gmain") != NULL ||
                strstr(comm, "pool-frida") != NULL ||
                strstr(comm, "gdbus") != NULL) {
                hit = 1;
            }
        }
        fclose(fp);
        if (hit) {
            break;
        }
    }
    closedir(dir);
    return hit;
}

JNIEXPORT jboolean JNICALL
Java_com_repl_shihuo_security_FridaGuard_nativeCheck(JNIEnv *env, jclass clazz) {
    (void) env;
    (void) clazz;
    if (scan_maps() || scan_threads()) {
        return JNI_TRUE;
    }
    return JNI_FALSE;
}
