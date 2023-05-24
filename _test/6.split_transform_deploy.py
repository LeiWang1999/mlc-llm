# from tvm.script import ir as I
# from tvm.script import tir as T
# from tvm.script import relax as R

@I.ir_module
class Module:
    @T.prim_func
    def encode(A: T.Buffer((T.int64(32000), T.int64(4096)), "float16"), w_gathered: T.Buffer((T.int64(32000), T.int64(512)), "uint32"), scale: T.Buffer((T.int64(32000), T.int64(128)), "float16")):
        T.func_attr({"op_pattern": 4, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        max_abs_value = T.alloc_buffer((T.int64(32000), T.int64(128)), "float16")
        for i, j, k in T.grid(T.int64(32000), T.int64(128), T.int64(32)):
            with T.block("max_abs_value"):
                v_i, v_j, v_k = T.axis.remap("SSR", [i, j, k])
                T.reads(A[v_i, v_j * T.int64(32) + v_k])
                T.writes(max_abs_value[v_i, v_j])
                with T.init():
                    max_abs_value[v_i, v_j] = T.float16(-65504)
                max_abs_value[v_i, v_j] = T.max(max_abs_value[v_i, v_j], T.if_then_else(v_j * T.int64(32) + v_k < T.int64(4096), T.fabs(A[v_i, v_j * T.int64(32) + v_k]), T.float16(-65504)))
        for i, j in T.grid(T.int64(32000), T.int64(128)):
            with T.block("scale"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(max_abs_value[v_i, v_j])
                T.writes(scale[v_i, v_j])
                scale[v_i, v_j] = T.max(max_abs_value[v_i, v_j], T.float16(0.0001)) * T.float16(0.14285714285714285)
        for i, j, k in T.grid(T.int64(32000), T.int64(512), T.int64(8)):
            with T.block("w_gathered"):
                v_i, v_j, v_k = T.axis.remap("SSR", [i, j, k])
                T.reads(A[v_i, v_j * T.int64(8) + v_k], scale[v_i, (v_j * T.int64(8) + v_k) // T.int64(32)])
                T.writes(w_gathered[v_i, v_j])
                with T.init():
                    w_gathered[v_i, v_j] = T.uint32(0)
                w_gathered[v_i, v_j] = T.bitwise_or(w_gathered[v_i, v_j], T.if_then_else(v_j * T.int64(8) + v_k < T.int64(4096), T.shift_left(T.Cast("uint32", T.min(T.max(T.round(A[v_i, v_j * T.int64(8) + v_k] / scale[v_i, (v_j * T.int64(8) + v_k) // T.int64(32)] + T.float16(7)), T.float16(0)), T.float16(14))), T.Cast("uint32", v_k) * T.uint32(4)), T.uint32(0)))

    @T.prim_func
    def encode1(A: T.Buffer((T.int64(4096), T.int64(4096)), "float16"), w_gathered: T.Buffer((T.int64(512), T.int64(4096)), "uint32"), compute: T.Buffer((T.int64(128), T.int64(4096)), "float16")):
        T.func_attr({"op_pattern": 4, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        max_abs_value = T.alloc_buffer((T.int64(4096), T.int64(128)), "float16")
        scale = T.alloc_buffer((T.int64(4096), T.int64(128)), "float16")
        for i, j, k in T.grid(T.int64(4096), T.int64(128), T.int64(32)):
            with T.block("max_abs_value"):
                v_i, v_j, v_k = T.axis.remap("SSR", [i, j, k])
                T.reads(A[v_i, v_j * T.int64(32) + v_k])
                T.writes(max_abs_value[v_i, v_j])
                with T.init():
                    max_abs_value[v_i, v_j] = T.float16(-65504)
                max_abs_value[v_i, v_j] = T.max(max_abs_value[v_i, v_j], T.if_then_else(v_j * T.int64(32) + v_k < T.int64(4096), T.fabs(A[v_i, v_j * T.int64(32) + v_k]), T.float16(-65504)))
        for i, j in T.grid(T.int64(4096), T.int64(128)):
            with T.block("scale"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(max_abs_value[v_i, v_j])
                T.writes(scale[v_i, v_j])
                scale[v_i, v_j] = T.max(max_abs_value[v_i, v_j], T.float16(0.0001)) * T.float16(0.14285714285714285)
        for j, i, k in T.grid(T.int64(512), T.int64(4096), T.int64(8)):
            with T.block("w_gathered"):
                v_j, v_i, v_k = T.axis.remap("SSR", [j, i, k])
                T.reads(A[v_i, v_j * T.int64(8) + v_k], scale[v_i, (v_j * T.int64(8) + v_k) // T.int64(32)])
                T.writes(w_gathered[v_j, v_i])
                with T.init():
                    w_gathered[v_j, v_i] = T.uint32(0)
                w_gathered[v_j, v_i] = T.bitwise_or(w_gathered[v_j, v_i], T.if_then_else(v_j * T.int64(8) + v_k < T.int64(4096), T.shift_left(T.Cast("uint32", T.min(T.max(T.round(A[v_i, v_j * T.int64(8) + v_k] / scale[v_i, (v_j * T.int64(8) + v_k) // T.int64(32)] + T.float16(7)), T.float16(0)), T.float16(14))), T.Cast("uint32", v_k) * T.uint32(4)), T.uint32(0)))
        for j, i in T.grid(T.int64(128), T.int64(4096)):
            with T.block("compute"):
                v_j, v_i = T.axis.remap("SS", [j, i])
                T.reads(scale[v_i, v_j])
                T.writes(compute[v_j, v_i])
                compute[v_j, v_i] = scale[v_i, v_j]

    @T.prim_func
    def encode2(A: T.Buffer((T.int64(11008), T.int64(4096)), "float16"), w_gathered: T.Buffer((T.int64(512), T.int64(11008)), "uint32"), compute: T.Buffer((T.int64(128), T.int64(11008)), "float16")):
        T.func_attr({"op_pattern": 4, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        max_abs_value = T.alloc_buffer((T.int64(11008), T.int64(128)), "float16")
        scale = T.alloc_buffer((T.int64(11008), T.int64(128)), "float16")
        for i, j, k in T.grid(T.int64(11008), T.int64(128), T.int64(32)):
            with T.block("max_abs_value"):
                v_i, v_j, v_k = T.axis.remap("SSR", [i, j, k])
                T.reads(A[v_i, v_j * T.int64(32) + v_k])
                T.writes(max_abs_value[v_i, v_j])
                with T.init():
                    max_abs_value[v_i, v_j] = T.float16(-65504)
                max_abs_value[v_i, v_j] = T.max(max_abs_value[v_i, v_j], T.if_then_else(v_j * T.int64(32) + v_k < T.int64(4096), T.fabs(A[v_i, v_j * T.int64(32) + v_k]), T.float16(-65504)))
        for i, j in T.grid(T.int64(11008), T.int64(128)):
            with T.block("scale"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(max_abs_value[v_i, v_j])
                T.writes(scale[v_i, v_j])
                scale[v_i, v_j] = T.max(max_abs_value[v_i, v_j], T.float16(0.0001)) * T.float16(0.14285714285714285)
        for j, i, k in T.grid(T.int64(512), T.int64(11008), T.int64(8)):
            with T.block("w_gathered"):
                v_j, v_i, v_k = T.axis.remap("SSR", [j, i, k])
                T.reads(A[v_i, v_j * T.int64(8) + v_k], scale[v_i, (v_j * T.int64(8) + v_k) // T.int64(32)])
                T.writes(w_gathered[v_j, v_i])
                with T.init():
                    w_gathered[v_j, v_i] = T.uint32(0)
                w_gathered[v_j, v_i] = T.bitwise_or(w_gathered[v_j, v_i], T.if_then_else(v_j * T.int64(8) + v_k < T.int64(4096), T.shift_left(T.Cast("uint32", T.min(T.max(T.round(A[v_i, v_j * T.int64(8) + v_k] / scale[v_i, (v_j * T.int64(8) + v_k) // T.int64(32)] + T.float16(7)), T.float16(0)), T.float16(14))), T.Cast("uint32", v_k) * T.uint32(4)), T.uint32(0)))
        for j, i in T.grid(T.int64(128), T.int64(11008)):
            with T.block("compute"):
                v_j, v_i = T.axis.remap("SS", [j, i])
                T.reads(scale[v_i, v_j])
                T.writes(compute[v_j, v_i])
                compute[v_j, v_i] = scale[v_i, v_j]

    @T.prim_func
    def encode3(A: T.Buffer((T.int64(4096), T.int64(11008)), "float16"), w_gathered: T.Buffer((T.int64(1376), T.int64(4096)), "uint32"), compute: T.Buffer((T.int64(344), T.int64(4096)), "float16")):
        T.func_attr({"op_pattern": 4, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        max_abs_value = T.alloc_buffer((T.int64(4096), T.int64(344)), "float16")
        scale = T.alloc_buffer((T.int64(4096), T.int64(344)), "float16")
        for i, j, k in T.grid(T.int64(4096), T.int64(344), T.int64(32)):
            with T.block("max_abs_value"):
                v_i, v_j, v_k = T.axis.remap("SSR", [i, j, k])
                T.reads(A[v_i, v_j * T.int64(32) + v_k])
                T.writes(max_abs_value[v_i, v_j])
                with T.init():
                    max_abs_value[v_i, v_j] = T.float16(-65504)
                max_abs_value[v_i, v_j] = T.max(max_abs_value[v_i, v_j], T.if_then_else(v_j * T.int64(32) + v_k < T.int64(11008), T.fabs(A[v_i, v_j * T.int64(32) + v_k]), T.float16(-65504)))
        for i, j in T.grid(T.int64(4096), T.int64(344)):
            with T.block("scale"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(max_abs_value[v_i, v_j])
                T.writes(scale[v_i, v_j])
                scale[v_i, v_j] = T.max(max_abs_value[v_i, v_j], T.float16(0.0001)) * T.float16(0.14285714285714285)
        for j, i, k in T.grid(T.int64(1376), T.int64(4096), T.int64(8)):
            with T.block("w_gathered"):
                v_j, v_i, v_k = T.axis.remap("SSR", [j, i, k])
                T.reads(A[v_i, v_j * T.int64(8) + v_k], scale[v_i, (v_j * T.int64(8) + v_k) // T.int64(32)])
                T.writes(w_gathered[v_j, v_i])
                with T.init():
                    w_gathered[v_j, v_i] = T.uint32(0)
                w_gathered[v_j, v_i] = T.bitwise_or(w_gathered[v_j, v_i], T.if_then_else(v_j * T.int64(8) + v_k < T.int64(11008), T.shift_left(T.Cast("uint32", T.min(T.max(T.round(A[v_i, v_j * T.int64(8) + v_k] / scale[v_i, (v_j * T.int64(8) + v_k) // T.int64(32)] + T.float16(7)), T.float16(0)), T.float16(14))), T.Cast("uint32", v_k) * T.uint32(4)), T.uint32(0)))
        for j, i in T.grid(T.int64(344), T.int64(4096)):
            with T.block("compute"):
                v_j, v_i = T.axis.remap("SS", [j, i])
                T.reads(scale[v_i, v_j])
                T.writes(compute[v_j, v_i])
                compute[v_j, v_i] = scale[v_i, v_j]

    @T.prim_func
    def encode4(A: T.Buffer((T.int64(32000), T.int64(4096)), "float16"), w_gathered: T.Buffer((T.int64(512), T.int64(32000)), "uint32"), compute: T.Buffer((T.int64(128), T.int64(32000)), "float16")):
        T.func_attr({"op_pattern": 4, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        max_abs_value = T.alloc_buffer((T.int64(32000), T.int64(128)), "float16")
        scale = T.alloc_buffer((T.int64(32000), T.int64(128)), "float16")
        for i, j, k in T.grid(T.int64(32000), T.int64(128), T.int64(32)):
            with T.block("max_abs_value"):
                v_i, v_j, v_k = T.axis.remap("SSR", [i, j, k])
                T.reads(A[v_i, v_j * T.int64(32) + v_k])
                T.writes(max_abs_value[v_i, v_j])
                with T.init():
                    max_abs_value[v_i, v_j] = T.float16(-65504)
                max_abs_value[v_i, v_j] = T.max(max_abs_value[v_i, v_j], T.if_then_else(v_j * T.int64(32) + v_k < T.int64(4096), T.fabs(A[v_i, v_j * T.int64(32) + v_k]), T.float16(-65504)))
        for i, j in T.grid(T.int64(32000), T.int64(128)):
            with T.block("scale"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(max_abs_value[v_i, v_j])
                T.writes(scale[v_i, v_j])
                scale[v_i, v_j] = T.max(max_abs_value[v_i, v_j], T.float16(0.0001)) * T.float16(0.14285714285714285)
        for j, i, k in T.grid(T.int64(512), T.int64(32000), T.int64(8)):
            with T.block("w_gathered"):
                v_j, v_i, v_k = T.axis.remap("SSR", [j, i, k])
                T.reads(A[v_i, v_j * T.int64(8) + v_k], scale[v_i, (v_j * T.int64(8) + v_k) // T.int64(32)])
                T.writes(w_gathered[v_j, v_i])
                with T.init():
                    w_gathered[v_j, v_i] = T.uint32(0)
                w_gathered[v_j, v_i] = T.bitwise_or(w_gathered[v_j, v_i], T.if_then_else(v_j * T.int64(8) + v_k < T.int64(4096), T.shift_left(T.Cast("uint32", T.min(T.max(T.round(A[v_i, v_j * T.int64(8) + v_k] / scale[v_i, (v_j * T.int64(8) + v_k) // T.int64(32)] + T.float16(7)), T.float16(0)), T.float16(14))), T.Cast("uint32", v_k) * T.uint32(4)), T.uint32(0)))
        for j, i in T.grid(T.int64(128), T.int64(32000)):
            with T.block("compute"):
                v_j, v_i = T.axis.remap("SS", [j, i])
                T.reads(scale[v_i, v_j])
                T.writes(compute[v_j, v_i])
                compute[v_j, v_i] = scale[v_i, v_j]

    @R.function
    def encoding_transform_params(params: R.Tuple(R.Tensor((32000, 4096), dtype="float16"), R.Tensor((4096, 4096), dtype="float16"), R.Tensor((4096, 4096), dtype="float16"), R.Tensor((4096, 4096), dtype="float16"), R.Tensor((4096, 4096), dtype="float16"), R.Tensor((11008, 4096), dtype="float16"), R.Tensor((4096, 11008), dtype="float16"), R.Tensor((11008, 4096), dtype="float16"), R.Tensor((4096,), dtype="float16"), R.Tensor((4096,), dtype="float16"), R.Tensor((4096,), dtype="float16"), R.Tensor((32000, 4096), dtype="float16"), R.Tensor((2048, 128), dtype="float16"), R.Tensor((2048, 128), dtype="float16"))) -> R.Tuple(R.Tensor((4096,), dtype="float16"), R.Tensor((4096,), dtype="float16"), R.Tensor((4096,), dtype="float16"), R.Tensor((2048, 128), dtype="float16"), R.Tensor((2048, 128), dtype="float16"), R.Tensor((32000, 512), dtype="uint32"), R.Tensor((32000, 128), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 11008), dtype="uint32"), R.Tensor((128, 11008), dtype="float16"), R.Tensor((512, 11008), dtype="uint32"), R.Tensor((128, 11008), dtype="float16"), R.Tensor((1376, 4096), dtype="uint32"), R.Tensor((344, 4096), dtype="float16"), R.Tensor((512, 32000), dtype="uint32"), R.Tensor((128, 32000), dtype="float16")):
        cls = Module
        with R.dataflow():
            lv: R.Tensor((4096,), dtype="float16") = params[8]
            lv1: R.Tensor((4096,), dtype="float16") = params[9]
            lv2: R.Tensor((4096,), dtype="float16") = params[10]
            lv3: R.Tensor((2048, 128), dtype="float16") = params[12]
            lv4: R.Tensor((2048, 128), dtype="float16") = params[13]
            lv5: R.Tensor((32000, 4096), dtype="float16") = params[0]
            lv53 = R.call_tir(cls.encode, (lv5,), out_sinfo=[R.Tensor((32000, 512), dtype="uint32"), R.Tensor((32000, 128), dtype="float16")])
            lv6: R.Tensor((32000, 512), dtype="uint32") = lv53[0]
            lv7: R.Tensor((32000, 128), dtype="float16") = lv53[1]
            lv8: R.Tensor((4096, 4096), dtype="float16") = params[1]
            lv58 = R.call_tir(cls.encode1, (lv8,), out_sinfo=[R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16")])
            lv9: R.Tensor((512, 4096), dtype="uint32") = lv58[0]
            lv10: R.Tensor((128, 4096), dtype="float16") = lv58[1]
            lv11: R.Tensor((4096, 4096), dtype="float16") = params[2]
            lv65 = R.call_tir(cls.encode1, (lv11,), out_sinfo=[R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16")])
            lv12: R.Tensor((512, 4096), dtype="uint32") = lv65[0]
            lv13: R.Tensor((128, 4096), dtype="float16") = lv65[1]
            lv14: R.Tensor((4096, 4096), dtype="float16") = params[3]
            lv72 = R.call_tir(cls.encode1, (lv14,), out_sinfo=[R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16")])
            lv15: R.Tensor((512, 4096), dtype="uint32") = lv72[0]
            lv16: R.Tensor((128, 4096), dtype="float16") = lv72[1]
            lv17: R.Tensor((4096, 4096), dtype="float16") = params[4]
            lv79 = R.call_tir(cls.encode1, (lv17,), out_sinfo=[R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16")])
            lv18: R.Tensor((512, 4096), dtype="uint32") = lv79[0]
            lv19: R.Tensor((128, 4096), dtype="float16") = lv79[1]
            lv20: R.Tensor((11008, 4096), dtype="float16") = params[5]
            lv86 = R.call_tir(cls.encode2, (lv20,), out_sinfo=[R.Tensor((512, 11008), dtype="uint32"), R.Tensor((128, 11008), dtype="float16")])
            lv21: R.Tensor((512, 11008), dtype="uint32") = lv86[0]
            lv22: R.Tensor((128, 11008), dtype="float16") = lv86[1]
            lv23: R.Tensor((11008, 4096), dtype="float16") = params[7]
            lv93 = R.call_tir(cls.encode2, (lv23,), out_sinfo=[R.Tensor((512, 11008), dtype="uint32"), R.Tensor((128, 11008), dtype="float16")])
            lv24: R.Tensor((512, 11008), dtype="uint32") = lv93[0]
            lv25: R.Tensor((128, 11008), dtype="float16") = lv93[1]
            lv26: R.Tensor((4096, 11008), dtype="float16") = params[6]
            lv100 = R.call_tir(cls.encode3, (lv26,), out_sinfo=[R.Tensor((1376, 4096), dtype="uint32"), R.Tensor((344, 4096), dtype="float16")])
            lv27: R.Tensor((1376, 4096), dtype="uint32") = lv100[0]
            lv28: R.Tensor((344, 4096), dtype="float16") = lv100[1]
            lv29: R.Tensor((32000, 4096), dtype="float16") = params[11]
            lv107 = R.call_tir(cls.encode4, (lv29,), out_sinfo=[R.Tensor((512, 32000), dtype="uint32"), R.Tensor((128, 32000), dtype="float16")])
            lv30: R.Tensor((512, 32000), dtype="uint32") = lv107[0]
            lv31: R.Tensor((128, 32000), dtype="float16") = lv107[1]
            gv: R.Tuple(R.Tensor((4096,), dtype="float16"), R.Tensor((4096,), dtype="float16"), R.Tensor((4096,), dtype="float16"), R.Tensor((2048, 128), dtype="float16"), R.Tensor((2048, 128), dtype="float16"), R.Tensor((32000, 512), dtype="uint32"), R.Tensor((32000, 128), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 11008), dtype="uint32"), R.Tensor((128, 11008), dtype="float16"), R.Tensor((512, 11008), dtype="uint32"), R.Tensor((128, 11008), dtype="float16"), R.Tensor((1376, 4096), dtype="uint32"), R.Tensor((344, 4096), dtype="float16"), R.Tensor((512, 32000), dtype="uint32"), R.Tensor((128, 32000), dtype="float16")) = lv, lv1, lv2, lv3, lv4, lv6, lv7, lv9, lv10, lv12, lv13, lv15, lv16, lv18, lv19, lv21, lv22, lv24, lv25, lv27, lv28, lv30, lv31
            R.output(gv)
        return gv


# from tvm.script import ir as I
# from tvm.script import tir as T
# from tvm.script import relax as R

@I.ir_module
class Module:
    @T.prim_func
    def NT_matmul1(var_A: T.handle, B: T.Buffer((T.int64(4096), T.int64(4096)), "float16"), var_NT_matmul: T.handle):
        T.func_attr({"op_pattern": 4, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (T.int64(1), n, T.int64(4096)), "float16")
        NT_matmul = T.match_buffer(var_NT_matmul, (T.int64(1), n, T.int64(4096)), "float16")
        # with T.block("root"):
        for i0, i1, i2, k in T.grid(T.int64(1), n, T.int64(4096), T.int64(4096)):
            with T.block("NT_matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(A[v_i0, v_i1, v_k], B[v_i2, v_k])
                T.writes(NT_matmul[v_i0, v_i1, v_i2])
                with T.init():
                    NT_matmul[v_i0, v_i1, v_i2] = T.float16(0)
                NT_matmul[v_i0, v_i1, v_i2] = NT_matmul[v_i0, v_i1, v_i2] + A[v_i0, v_i1, v_k] * B[v_i2, v_k]

    @T.prim_func
    def decode4(A: T.Buffer((T.int64(512), T.int64(4096)), "uint32"), B: T.Buffer((T.int64(128), T.int64(4096)), "float16"), T_transpose: T.Buffer((T.int64(4096), T.int64(4096)), "float16")):
        T.func_attr({"op_pattern": 2, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        decode = T.alloc_buffer((T.int64(4096), T.int64(4096)), "float16")
        for i, j in T.grid(T.int64(4096), T.int64(4096)):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(A[v_i // T.int64(8), v_j], B[v_i // T.int64(32), v_j])
                T.writes(decode[v_i, v_j])
                decode[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(A[v_i // T.int64(8), v_j], T.Cast("uint32", v_i % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * B[v_i // T.int64(32), v_j]
        for ax0, ax1 in T.grid(T.int64(4096), T.int64(4096)):
            with T.block("T_transpose"):
                v_ax0, v_ax1 = T.axis.remap("SS", [ax0, ax1])
                T.reads(decode[v_ax1, v_ax0])
                T.writes(T_transpose[v_ax0, v_ax1])
                T_transpose[v_ax0, v_ax1] = decode[v_ax1, v_ax0]

    @T.prim_func
    def decode5(A: T.Buffer((T.int64(512), T.int64(11008)), "uint32"), B: T.Buffer((T.int64(128), T.int64(11008)), "float16"), T_transpose: T.Buffer((T.int64(11008), T.int64(4096)), "float16")):
        T.func_attr({"op_pattern": 2, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        decode = T.alloc_buffer((T.int64(4096), T.int64(11008)), "float16")
        for i, j in T.grid(T.int64(4096), T.int64(11008)):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(A[v_i // T.int64(8), v_j], B[v_i // T.int64(32), v_j])
                T.writes(decode[v_i, v_j])
                decode[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(A[v_i // T.int64(8), v_j], T.Cast("uint32", v_i % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * B[v_i // T.int64(32), v_j]
        for ax0, ax1 in T.grid(T.int64(11008), T.int64(4096)):
            with T.block("T_transpose"):
                v_ax0, v_ax1 = T.axis.remap("SS", [ax0, ax1])
                T.reads(decode[v_ax1, v_ax0])
                T.writes(T_transpose[v_ax0, v_ax1])
                T_transpose[v_ax0, v_ax1] = decode[v_ax1, v_ax0]

    @T.prim_func
    def decode6(A: T.Buffer((T.int64(1376), T.int64(4096)), "uint32"), B: T.Buffer((T.int64(344), T.int64(4096)), "float16"), T_transpose: T.Buffer((T.int64(4096), T.int64(11008)), "float16")):
        T.func_attr({"op_pattern": 2, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        decode = T.alloc_buffer((T.int64(11008), T.int64(4096)), "float16")
        for i, j in T.grid(T.int64(11008), T.int64(4096)):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(A[v_i // T.int64(8), v_j], B[v_i // T.int64(32), v_j])
                T.writes(decode[v_i, v_j])
                decode[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(A[v_i // T.int64(8), v_j], T.Cast("uint32", v_i % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * B[v_i // T.int64(32), v_j]
        for ax0, ax1 in T.grid(T.int64(4096), T.int64(11008)):
            with T.block("T_transpose"):
                v_ax0, v_ax1 = T.axis.remap("SS", [ax0, ax1])
                T.reads(decode[v_ax1, v_ax0])
                T.writes(T_transpose[v_ax0, v_ax1])
                T_transpose[v_ax0, v_ax1] = decode[v_ax1, v_ax0]

    @T.prim_func
    def divide(A: T.Buffer((T.int64(1), T.int64(1), T.int64(32000)), "float32"), B: T.Buffer((), "float32"), T_divide: T.Buffer((T.int64(1), T.int64(1), T.int64(32000)), "float32")):
        T.func_attr({"op_pattern": 0, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        for ax0, ax1, ax2 in T.grid(T.int64(1), T.int64(1), T.int64(32000)):
            with T.block("T_divide"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(A[v_ax0, v_ax1, v_ax2], B[()])
                T.writes(T_divide[v_ax0, v_ax1, v_ax2])
                T_divide[v_ax0, v_ax1, v_ax2] = A[v_ax0, v_ax1, v_ax2] / B[()]

    @T.prim_func
    def extend_te(var_A: T.handle, var_concat_te: T.handle):
        T.func_attr({"op_pattern": 8, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (T.int64(1), T.int64(1), n, n), "float16")
        m = T.int64()
        concat_te = T.match_buffer(var_concat_te, (T.int64(1), T.int64(1), n, m), "float16")
        # with T.block("root"):
        for b, _, i, j in T.grid(T.int64(1), T.int64(1), n, m):
            with T.block("concat_te"):
                v_b, v__, v_i, v_j = T.axis.remap("SSSS", [b, _, i, j])
                T.reads(A[v_b, v__, v_i, v_j + n - m])
                T.writes(concat_te[v_b, v__, v_i, v_j])
                concat_te[v_b, v__, v_i, v_j] = T.if_then_else(v_j < m - n, T.float16(65504), A[v_b, v__, v_i, v_j + n - m])

    @T.prim_func
    def fused_NT_matmul1_add1(p_lv41: T.handle, lv84: T.Buffer((T.int64(4096), T.int64(4096)), "float16"), p_lv2: T.handle, p_output0: T.handle):
        T.func_attr({"tir.noalias": T.bool(True)})
        n = T.int64()
        lv41 = T.match_buffer(p_lv41, (T.int64(1), n, T.int64(4096)), "float16")
        lv2 = T.match_buffer(p_lv2, (T.int64(1), n, T.int64(4096)), "float16")
        var_T_add_intermediate = T.match_buffer(p_output0, (T.int64(1), n, T.int64(4096)), "float16")
        # with T.block("root"):
        var_NT_matmul_intermediate = T.alloc_buffer((T.int64(1), n, T.int64(4096)), "float16")
        for i0, i1, i2, k in T.grid(T.int64(1), n, T.int64(4096), T.int64(4096)):
            with T.block("NT_matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv41[v_i0, v_i1, v_k], lv84[v_i2, v_k])
                T.writes(var_NT_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = var_NT_matmul_intermediate[v_i0, v_i1, v_i2] + lv41[v_i0, v_i1, v_k] * lv84[v_i2, v_k]
        for ax0, ax1, ax2 in T.grid(T.int64(1), n, T.int64(4096)):
            with T.block("T_add"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(lv2[v_ax0, v_ax1, v_ax2], var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2])
                T.writes(var_T_add_intermediate[v_ax0, v_ax1, v_ax2])
                var_T_add_intermediate[v_ax0, v_ax1, v_ax2] = lv2[v_ax0, v_ax1, v_ax2] + var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2]

    @T.prim_func
    def fused_NT_matmul2_divide2_maximum1_minimum1_cast3(p_lv28: T.handle, p_lv29: T.handle, p_lv5: T.handle, p_output0: T.handle):
        T.func_attr({"tir.noalias": T.bool(True)})
        n = T.int64()
        lv28 = T.match_buffer(p_lv28, (T.int64(1), T.int64(32), n, T.int64(128)), "float16")
        m = T.int64()
        lv29 = T.match_buffer(p_lv29, (T.int64(1), T.int64(32), m, T.int64(128)), "float16")
        lv5 = T.match_buffer(p_lv5, (T.int64(1), T.int64(1), n, m), "float16")
        var_compute_intermediate = T.match_buffer(p_output0, (T.int64(1), T.int64(32), n, m))
        # with T.block("root"):
        var_NT_matmul_intermediate = T.alloc_buffer((T.int64(1), T.int64(32), n, m), "float16")
        var_T_divide_intermediate = T.alloc_buffer((T.int64(1), T.int64(32), n, m), "float16")
        var_T_maximum_intermediate = T.alloc_buffer((T.int64(1), T.int64(32), n, m), "float16")
        var_T_minimum_intermediate = T.alloc_buffer((T.int64(1), T.int64(32), n, m), "float16")
        for i0, i1, i2, i3, k in T.grid(T.int64(1), T.int64(32), n, m, T.int64(128)):
            with T.block("NT_matmul"):
                v_i0, v_i1, v_i2, v_i3, v_k = T.axis.remap("SSSSR", [i0, i1, i2, i3, k])
                T.reads(lv28[v_i0, v_i1, v_i2, v_k], lv29[v_i0, v_i1, v_i3, v_k])
                T.writes(var_NT_matmul_intermediate[v_i0, v_i1, v_i2, v_i3])
                with T.init():
                    var_NT_matmul_intermediate[v_i0, v_i1, v_i2, v_i3] = T.float16(0)
                var_NT_matmul_intermediate[v_i0, v_i1, v_i2, v_i3] = var_NT_matmul_intermediate[v_i0, v_i1, v_i2, v_i3] + lv28[v_i0, v_i1, v_i2, v_k] * lv29[v_i0, v_i1, v_i3, v_k]
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), T.int64(32), n, m):
            with T.block("T_divide"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                T.writes(var_T_divide_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                var_T_divide_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] = var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] * T.float16(0.088397790055248615)
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), T.int64(32), n, m):
            with T.block("T_maximum"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(var_T_divide_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                T.writes(var_T_maximum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                var_T_maximum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] = T.max(var_T_divide_intermediate[v_ax0, v_ax1, v_ax2, v_ax3], T.float16(-65504))
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), T.int64(32), n, m):
            with T.block("T_minimum"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(var_T_maximum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3], lv5[v_ax0, T.int64(0), v_ax2, v_ax3])
                T.writes(var_T_minimum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                var_T_minimum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] = T.min(var_T_maximum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3], lv5[v_ax0, T.int64(0), v_ax2, v_ax3])
        for i0, i1, i2, i3 in T.grid(T.int64(1), T.int64(32), n, m):
            with T.block("compute"):
                v_i0, v_i1, v_i2, v_i3 = T.axis.remap("SSSS", [i0, i1, i2, i3])
                T.reads(var_T_minimum_intermediate[v_i0, v_i1, v_i2, v_i3])
                T.writes(var_compute_intermediate[v_i0, v_i1, v_i2, v_i3])
                var_compute_intermediate[v_i0, v_i1, v_i2, v_i3] = T.Cast("float32", var_T_minimum_intermediate[v_i0, v_i1, v_i2, v_i3])

    @T.prim_func
    def fused_NT_matmul3_multiply1(p_lv45: T.handle, lv98: T.Buffer((T.int64(11008), T.int64(4096)), "float16"), p_lv50: T.handle, p_output0: T.handle):
        T.func_attr({"tir.noalias": T.bool(True)})
        n = T.int64()
        lv45 = T.match_buffer(p_lv45, (T.int64(1), n, T.int64(4096)), "float16")
        lv50 = T.match_buffer(p_lv50, (T.int64(1), n, T.int64(11008)), "float16")
        var_T_multiply_intermediate = T.match_buffer(p_output0, (T.int64(1), n, T.int64(11008)), "float16")
        # with T.block("root"):
        var_NT_matmul_intermediate = T.alloc_buffer((T.int64(1), n, T.int64(11008)), "float16")
        for i0, i1, i2, k in T.grid(T.int64(1), n, T.int64(11008), T.int64(4096)):
            with T.block("NT_matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv45[v_i0, v_i1, v_k], lv98[v_i2, v_k])
                T.writes(var_NT_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = var_NT_matmul_intermediate[v_i0, v_i1, v_i2] + lv45[v_i0, v_i1, v_k] * lv98[v_i2, v_k]
        for ax0, ax1, ax2 in T.grid(T.int64(1), n, T.int64(11008)):
            with T.block("T_multiply"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(lv50[v_ax0, v_ax1, v_ax2], var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2])
                T.writes(var_T_multiply_intermediate[v_ax0, v_ax1, v_ax2])
                var_T_multiply_intermediate[v_ax0, v_ax1, v_ax2] = lv50[v_ax0, v_ax1, v_ax2] * var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2]

    @T.prim_func
    def fused_NT_matmul3_silu1(p_lv45: T.handle, lv91: T.Buffer((T.int64(11008), T.int64(4096)), "float16"), p_output0: T.handle):
        T.func_attr({"tir.noalias": T.bool(True)})
        n = T.int64()
        lv45 = T.match_buffer(p_lv45, (T.int64(1), n, T.int64(4096)), "float16")
        var_T_multiply_intermediate = T.match_buffer(p_output0, (T.int64(1), n, T.int64(11008)), "float16")
        # with T.block("root"):
        var_NT_matmul_intermediate = T.alloc_buffer((T.int64(1), n, T.int64(11008)), "float16")
        compute = T.alloc_buffer((T.int64(1), n, T.int64(11008)), "float16")
        for i0, i1, i2, k in T.grid(T.int64(1), n, T.int64(11008), T.int64(4096)):
            with T.block("NT_matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv45[v_i0, v_i1, v_k], lv91[v_i2, v_k])
                T.writes(var_NT_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = var_NT_matmul_intermediate[v_i0, v_i1, v_i2] + lv45[v_i0, v_i1, v_k] * lv91[v_i2, v_k]
        for i0, i1, i2 in T.grid(T.int64(1), n, T.int64(11008)):
            with T.block("compute"):
                v_i0, v_i1, v_i2 = T.axis.remap("SSS", [i0, i1, i2])
                T.reads(var_NT_matmul_intermediate[v_i0, v_i1, v_i2])
                T.writes(compute[v_i0, v_i1, v_i2])
                compute[v_i0, v_i1, v_i2] = T.sigmoid(var_NT_matmul_intermediate[v_i0, v_i1, v_i2])
        for ax0, ax1, ax2 in T.grid(T.int64(1), n, T.int64(11008)):
            with T.block("T_multiply"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2], compute[v_ax0, v_ax1, v_ax2])
                T.writes(var_T_multiply_intermediate[v_ax0, v_ax1, v_ax2])
                var_T_multiply_intermediate[v_ax0, v_ax1, v_ax2] = var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2] * compute[v_ax0, v_ax1, v_ax2]

    @T.prim_func
    def fused_NT_matmul4_add1(p_lv51: T.handle, lv105: T.Buffer((T.int64(4096), T.int64(11008)), "float16"), p_lv44: T.handle, p_output0: T.handle):
        T.func_attr({"tir.noalias": T.bool(True)})
        n = T.int64()
        lv51 = T.match_buffer(p_lv51, (T.int64(1), n, T.int64(11008)), "float16")
        lv44 = T.match_buffer(p_lv44, (T.int64(1), n, T.int64(4096)), "float16")
        var_T_add_intermediate = T.match_buffer(p_output0, (T.int64(1), n, T.int64(4096)), "float16")
        # with T.block("root"):
        var_NT_matmul_intermediate = T.alloc_buffer((T.int64(1), n, T.int64(4096)), "float16")
        for i0, i1, i2, k in T.grid(T.int64(1), n, T.int64(4096), T.int64(11008)):
            with T.block("NT_matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv51[v_i0, v_i1, v_k], lv105[v_i2, v_k])
                T.writes(var_NT_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_NT_matmul_intermediate[v_i0, v_i1, v_i2] = var_NT_matmul_intermediate[v_i0, v_i1, v_i2] + lv51[v_i0, v_i1, v_k] * lv105[v_i2, v_k]
        for ax0, ax1, ax2 in T.grid(T.int64(1), n, T.int64(4096)):
            with T.block("T_add"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(lv44[v_ax0, v_ax1, v_ax2], var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2])
                T.writes(var_T_add_intermediate[v_ax0, v_ax1, v_ax2])
                var_T_add_intermediate[v_ax0, v_ax1, v_ax2] = lv44[v_ax0, v_ax1, v_ax2] + var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2]

    @T.prim_func
    def fused_decode1_fused_matmul3_multiply(lv38: T.Buffer((T.int64(512), T.int64(11008)), "uint32"), lv39: T.Buffer((T.int64(128), T.int64(11008)), "float16"), lv103: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), lv4: T.Buffer((T.int64(1), T.int64(1), T.int64(11008)), "float16"), p_output0_intermediate: T.Buffer((T.int64(1), T.int64(1), T.int64(11008)), "float16")):
        T.func_attr({"tir.noalias": T.bool(True)})
        # with T.block("root"):
        var_decode_intermediate = T.alloc_buffer((T.int64(4096), T.int64(11008)), "float16")
        var_matmul_intermediate = T.alloc_buffer((T.int64(1), T.int64(1), T.int64(11008)), "float16")
        for i, j in T.grid(T.int64(4096), T.int64(11008)):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv38[v_i // T.int64(8), v_j], lv39[v_i // T.int64(32), v_j])
                T.writes(var_decode_intermediate[v_i, v_j])
                var_decode_intermediate[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv38[v_i // T.int64(8), v_j], T.Cast("uint32", v_i % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * lv39[v_i // T.int64(32), v_j]
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(1), T.int64(11008), T.int64(4096)):
            with T.block("matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv103[v_i0, v_i1, v_k], var_decode_intermediate[v_k, v_i2])
                T.writes(var_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_matmul_intermediate[v_i0, v_i1, v_i2] = var_matmul_intermediate[v_i0, v_i1, v_i2] + lv103[v_i0, v_i1, v_k] * var_decode_intermediate[v_k, v_i2]
        for ax0, ax1, ax2 in T.grid(T.int64(1), T.int64(1), T.int64(11008)):
            with T.block("T_multiply"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(lv4[v_ax0, v_ax1, v_ax2], var_matmul_intermediate[v_ax0, v_ax1, v_ax2])
                T.writes(p_output0_intermediate[v_ax0, v_ax1, v_ax2])
                p_output0_intermediate[v_ax0, v_ax1, v_ax2] = lv4[v_ax0, v_ax1, v_ax2] * var_matmul_intermediate[v_ax0, v_ax1, v_ax2]

    @T.prim_func
    def fused_decode1_fused_matmul3_silu(lv32: T.Buffer((T.int64(512), T.int64(11008)), "uint32"), lv33: T.Buffer((T.int64(128), T.int64(11008)), "float16"), lv103: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), p_output0_intermediate: T.Buffer((T.int64(1), T.int64(1), T.int64(11008)), "float16")):
        T.func_attr({"tir.noalias": T.bool(True)})
        # with T.block("root"):
        var_decode_intermediate = T.alloc_buffer((T.int64(4096), T.int64(11008)), "float16")
        var_matmul_intermediate = T.alloc_buffer((T.int64(1), T.int64(1), T.int64(11008)), "float16")
        compute = T.alloc_buffer((T.int64(1), T.int64(1), T.int64(11008)), "float16")
        for i, j in T.grid(T.int64(4096), T.int64(11008)):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv32[v_i // T.int64(8), v_j], lv33[v_i // T.int64(32), v_j])
                T.writes(var_decode_intermediate[v_i, v_j])
                var_decode_intermediate[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv32[v_i // T.int64(8), v_j], T.Cast("uint32", v_i % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * lv33[v_i // T.int64(32), v_j]
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(1), T.int64(11008), T.int64(4096)):
            with T.block("matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv103[v_i0, v_i1, v_k], var_decode_intermediate[v_k, v_i2])
                T.writes(var_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_matmul_intermediate[v_i0, v_i1, v_i2] = var_matmul_intermediate[v_i0, v_i1, v_i2] + lv103[v_i0, v_i1, v_k] * var_decode_intermediate[v_k, v_i2]
        for i0, i1, i2 in T.grid(T.int64(1), T.int64(1), T.int64(11008)):
            with T.block("compute"):
                v_i0, v_i1, v_i2 = T.axis.remap("SSS", [i0, i1, i2])
                T.reads(var_matmul_intermediate[v_i0, v_i1, v_i2])
                T.writes(compute[v_i0, v_i1, v_i2])
                compute[v_i0, v_i1, v_i2] = T.sigmoid(var_matmul_intermediate[v_i0, v_i1, v_i2])
        for ax0, ax1, ax2 in T.grid(T.int64(1), T.int64(1), T.int64(11008)):
            with T.block("T_multiply"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(var_matmul_intermediate[v_ax0, v_ax1, v_ax2], compute[v_ax0, v_ax1, v_ax2])
                T.writes(p_output0_intermediate[v_ax0, v_ax1, v_ax2])
                p_output0_intermediate[v_ax0, v_ax1, v_ax2] = var_matmul_intermediate[v_ax0, v_ax1, v_ax2] * compute[v_ax0, v_ax1, v_ax2]

    @T.prim_func
    def fused_decode2_fused_matmul4_add(lv44: T.Buffer((T.int64(1376), T.int64(4096)), "uint32"), lv45: T.Buffer((T.int64(344), T.int64(4096)), "float16"), lv6: T.Buffer((T.int64(1), T.int64(1), T.int64(11008)), "float16"), lv4: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), p_output0_intermediate: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")):
        T.func_attr({"tir.noalias": T.bool(True)})
        # with T.block("root"):
        var_decode_intermediate = T.alloc_buffer((T.int64(11008), T.int64(4096)), "float16")
        var_matmul_intermediate = T.alloc_buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")
        for i, j in T.grid(T.int64(11008), T.int64(4096)):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv44[v_i // T.int64(8), v_j], lv45[v_i // T.int64(32), v_j])
                T.writes(var_decode_intermediate[v_i, v_j])
                var_decode_intermediate[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv44[v_i // T.int64(8), v_j], T.Cast("uint32", v_i % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * lv45[v_i // T.int64(32), v_j]
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(1), T.int64(4096), T.int64(11008)):
            with T.block("matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv6[v_i0, v_i1, v_k], var_decode_intermediate[v_k, v_i2])
                T.writes(var_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_matmul_intermediate[v_i0, v_i1, v_i2] = var_matmul_intermediate[v_i0, v_i1, v_i2] + lv6[v_i0, v_i1, v_k] * var_decode_intermediate[v_k, v_i2]
        for ax0, ax1, ax2 in T.grid(T.int64(1), T.int64(1), T.int64(4096)):
            with T.block("T_add"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(lv4[v_ax0, v_ax1, v_ax2], var_matmul_intermediate[v_ax0, v_ax1, v_ax2])
                T.writes(p_output0_intermediate[v_ax0, v_ax1, v_ax2])
                p_output0_intermediate[v_ax0, v_ax1, v_ax2] = lv4[v_ax0, v_ax1, v_ax2] + var_matmul_intermediate[v_ax0, v_ax1, v_ax2]

    @T.prim_func
    def fused_decode3_fused_matmul5_cast2(lv110: T.Buffer((T.int64(512), T.int64(32000)), "uint32"), lv111: T.Buffer((T.int64(128), T.int64(32000)), "float16"), lv56: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), p_output0_intermediate: T.Buffer((T.int64(1), T.int64(1), T.int64(32000)), "float32")):
        T.func_attr({"tir.noalias": T.bool(True)})
        # with T.block("root"):
        var_decode_intermediate = T.alloc_buffer((T.int64(4096), T.int64(32000)), "float16")
        var_matmul_intermediate = T.alloc_buffer((T.int64(1), T.int64(1), T.int64(32000)), "float16")
        for i, j in T.grid(T.int64(4096), T.int64(32000)):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv110[v_i // T.int64(8), v_j], lv111[v_i // T.int64(32), v_j])
                T.writes(var_decode_intermediate[v_i, v_j])
                var_decode_intermediate[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv110[v_i // T.int64(8), v_j], T.Cast("uint32", v_i % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * lv111[v_i // T.int64(32), v_j]
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(1), T.int64(32000), T.int64(4096)):
            with T.block("matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv56[v_i0, v_i1, v_k], var_decode_intermediate[v_k, v_i2])
                T.writes(var_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_matmul_intermediate[v_i0, v_i1, v_i2] = var_matmul_intermediate[v_i0, v_i1, v_i2] + lv56[v_i0, v_i1, v_k] * var_decode_intermediate[v_k, v_i2]
        for i0, i1, i2 in T.grid(T.int64(1), T.int64(1), T.int64(32000)):
            with T.block("compute"):
                v_i0, v_i1, v_i2 = T.axis.remap("SSS", [i0, i1, i2])
                T.reads(var_matmul_intermediate[v_i0, v_i1, v_i2])
                T.writes(p_output0_intermediate[v_i0, v_i1, v_i2])
                p_output0_intermediate[v_i0, v_i1, v_i2] = T.Cast("float32", var_matmul_intermediate[v_i0, v_i1, v_i2])

    @T.prim_func
    def fused_decode_fused_matmul1_add(lv26: T.Buffer((T.int64(512), T.int64(4096)), "uint32"), lv27: T.Buffer((T.int64(128), T.int64(4096)), "float16"), lv3: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), lv62: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), p_output0_intermediate: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")):
        T.func_attr({"tir.noalias": T.bool(True)})
        # with T.block("root"):
        var_decode_intermediate = T.alloc_buffer((T.int64(4096), T.int64(4096)), "float16")
        var_matmul_intermediate = T.alloc_buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")
        for i, j in T.grid(T.int64(4096), T.int64(4096)):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv26[v_i // T.int64(8), v_j], lv27[v_i // T.int64(32), v_j])
                T.writes(var_decode_intermediate[v_i, v_j])
                var_decode_intermediate[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv26[v_i // T.int64(8), v_j], T.Cast("uint32", v_i % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * lv27[v_i // T.int64(32), v_j]
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(1), T.int64(4096), T.int64(4096)):
            with T.block("matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv3[v_i0, v_i1, v_k], var_decode_intermediate[v_k, v_i2])
                T.writes(var_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_matmul_intermediate[v_i0, v_i1, v_i2] = var_matmul_intermediate[v_i0, v_i1, v_i2] + lv3[v_i0, v_i1, v_k] * var_decode_intermediate[v_k, v_i2]
        for ax0, ax1, ax2 in T.grid(T.int64(1), T.int64(1), T.int64(4096)):
            with T.block("T_add"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(lv62[v_ax0, v_ax1, v_ax2], var_matmul_intermediate[v_ax0, v_ax1, v_ax2])
                T.writes(p_output0_intermediate[v_ax0, v_ax1, v_ax2])
                p_output0_intermediate[v_ax0, v_ax1, v_ax2] = lv62[v_ax0, v_ax1, v_ax2] + var_matmul_intermediate[v_ax0, v_ax1, v_ax2]

    @T.prim_func
    def fused_decode_matmul1(lv8: T.Buffer((T.int64(512), T.int64(4096)), "uint32"), lv9: T.Buffer((T.int64(128), T.int64(4096)), "float16"), lv64: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), var_matmul_intermediate: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")):
        T.func_attr({"tir.noalias": T.bool(True)})
        # with T.block("root"):
        var_decode_intermediate = T.alloc_buffer((T.int64(4096), T.int64(4096)), "float16")
        for i, j in T.grid(T.int64(4096), T.int64(4096)):
            with T.block("decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(lv8[v_i // T.int64(8), v_j], lv9[v_i // T.int64(32), v_j])
                T.writes(var_decode_intermediate[v_i, v_j])
                var_decode_intermediate[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(lv8[v_i // T.int64(8), v_j], T.Cast("uint32", v_i % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * lv9[v_i // T.int64(32), v_j]
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(1), T.int64(4096), T.int64(4096)):
            with T.block("matmul"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv64[v_i0, v_i1, v_k], var_decode_intermediate[v_k, v_i2])
                T.writes(var_matmul_intermediate[v_i0, v_i1, v_i2])
                with T.init():
                    var_matmul_intermediate[v_i0, v_i1, v_i2] = T.float16(0)
                var_matmul_intermediate[v_i0, v_i1, v_i2] = var_matmul_intermediate[v_i0, v_i1, v_i2] + lv64[v_i0, v_i1, v_k] * var_decode_intermediate[v_k, v_i2]

    @T.prim_func
    def fused_full_NT_matmul_divide1_maximum_minimum_cast(lv86: T.Buffer((T.int64(1), T.int64(32), T.int64(1), T.int64(128)), "float16"), p_lv87: T.handle, p_output0: T.handle):
        T.func_attr({"tir.noalias": T.bool(True)})
        n = T.int64()
        lv87 = T.match_buffer(p_lv87, (T.int64(1), T.int64(32), n, T.int64(128)), "float16")
        var_compute_intermediate = T.match_buffer(p_output0, (T.int64(1), T.int64(32), T.int64(1), n))
        # with T.block("root"):
        var_T_full_intermediate = T.alloc_buffer((T.int64(1), T.int64(1), T.int64(1), n), "float16")
        var_NT_matmul_intermediate = T.alloc_buffer((T.int64(1), T.int64(32), T.int64(1), n), "float16")
        var_T_divide_intermediate = T.alloc_buffer((T.int64(1), T.int64(32), T.int64(1), n), "float16")
        var_T_maximum_intermediate = T.alloc_buffer((T.int64(1), T.int64(32), T.int64(1), n), "float16")
        var_T_minimum_intermediate = T.alloc_buffer((T.int64(1), T.int64(32), T.int64(1), n), "float16")
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), T.int64(1), T.int64(1), n):
            with T.block("T_full"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads()
                T.writes(var_T_full_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                var_T_full_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] = T.float16(65504)
        for i0, i1, i2, i3, k in T.grid(T.int64(1), T.int64(32), T.int64(1), n, T.int64(128)):
            with T.block("NT_matmul"):
                v_i0, v_i1, v_i2, v_i3, v_k = T.axis.remap("SSSSR", [i0, i1, i2, i3, k])
                T.reads(lv86[v_i0, v_i1, v_i2, v_k], lv87[v_i0, v_i1, v_i3, v_k])
                T.writes(var_NT_matmul_intermediate[v_i0, v_i1, v_i2, v_i3])
                with T.init():
                    var_NT_matmul_intermediate[v_i0, v_i1, v_i2, v_i3] = T.float16(0)
                var_NT_matmul_intermediate[v_i0, v_i1, v_i2, v_i3] = var_NT_matmul_intermediate[v_i0, v_i1, v_i2, v_i3] + lv86[v_i0, v_i1, v_i2, v_k] * lv87[v_i0, v_i1, v_i3, v_k]
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), T.int64(32), T.int64(1), n):
            with T.block("T_divide"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                T.writes(var_T_divide_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                var_T_divide_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] = var_NT_matmul_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] * T.float16(0.088397790055248615)
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), T.int64(32), T.int64(1), n):
            with T.block("T_maximum"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(var_T_divide_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                T.writes(var_T_maximum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                var_T_maximum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] = T.max(var_T_divide_intermediate[v_ax0, v_ax1, v_ax2, v_ax3], T.float16(-65504))
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), T.int64(32), T.int64(1), n):
            with T.block("T_minimum"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(var_T_maximum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3], var_T_full_intermediate[v_ax0, T.int64(0), v_ax2, v_ax3])
                T.writes(var_T_minimum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                var_T_minimum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] = T.min(var_T_maximum_intermediate[v_ax0, v_ax1, v_ax2, v_ax3], var_T_full_intermediate[v_ax0, T.int64(0), v_ax2, v_ax3])
        for i0, i1, i2, i3 in T.grid(T.int64(1), T.int64(32), T.int64(1), n):
            with T.block("compute"):
                v_i0, v_i1, v_i2, v_i3 = T.axis.remap("SSSS", [i0, i1, i2, i3])
                T.reads(var_T_minimum_intermediate[v_i0, v_i1, v_i2, v_i3])
                T.writes(var_compute_intermediate[v_i0, v_i1, v_i2, v_i3])
                var_compute_intermediate[v_i0, v_i1, v_i2, v_i3] = T.Cast("float32", var_T_minimum_intermediate[v_i0, v_i1, v_i2, v_i3])

    @T.prim_func
    def fused_min_max_triu_te_broadcast_to(p_output0: T.handle, n: T.int64):
        T.func_attr({"tir.noalias": T.bool(True)})
        var_T_broadcast_to_intermediate = T.match_buffer(p_output0, (T.int64(1), T.int64(1), n, n), "float16")
        # with T.block("root"):
        var_make_diag_mask_te_intermediate = T.alloc_buffer((n, n), "float16")
        for i, j in T.grid(n, n):
            with T.block("make_diag_mask_te"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads()
                T.writes(var_make_diag_mask_te_intermediate[v_i, v_j])
                var_make_diag_mask_te_intermediate[v_i, v_j] = T.Select(v_i < v_j, T.float16(-65504), T.float16(65504))
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), T.int64(1), n, n):
            with T.block("T_broadcast_to"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(var_make_diag_mask_te_intermediate[v_ax2, v_ax3])
                T.writes(var_T_broadcast_to_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                var_T_broadcast_to_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] = var_make_diag_mask_te_intermediate[v_ax2, v_ax3]

    @T.prim_func
    def fused_reshape2_squeeze(lv72: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), var_T_squeeze_intermediate: T.Buffer((T.int64(1), T.int64(32), T.int64(128)), "float16")):
        T.func_attr({"tir.noalias": T.bool(True)})
        # with T.block("root"):
        var_T_reshape_intermediate = T.alloc_buffer((T.int64(1), T.int64(1), T.int64(32), T.int64(128)), "float16")
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), T.int64(1), T.int64(32), T.int64(128)):
            with T.block("T_reshape"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(lv72[T.int64(0), T.int64(0), (v_ax2 * T.int64(128) + v_ax3) % T.int64(4096)])
                T.writes(var_T_reshape_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                var_T_reshape_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] = lv72[T.int64(0), T.int64(0), (v_ax2 * T.int64(128) + v_ax3) % T.int64(4096)]
        for ax0, ax1, ax2 in T.grid(T.int64(1), T.int64(32), T.int64(128)):
            with T.block("T_squeeze"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(var_T_reshape_intermediate[T.int64(0), v_ax0, v_ax1, v_ax2])
                T.writes(var_T_squeeze_intermediate[v_ax0, v_ax1, v_ax2])
                var_T_squeeze_intermediate[v_ax0, v_ax1, v_ax2] = var_T_reshape_intermediate[T.int64(0), v_ax0, v_ax1, v_ax2]

    @T.prim_func
    def fused_softmax1_cast1(p_lv94: T.handle, p_output0: T.handle):
        T.func_attr({"tir.noalias": T.bool(True)})
        n = T.int64()
        lv94 = T.match_buffer(p_lv94, (T.int64(1), T.int64(32), T.int64(1), n))
        var_compute_intermediate = T.match_buffer(p_output0, (T.int64(1), T.int64(32), T.int64(1), n), "float16")
        # with T.block("root"):
        T_softmax_maxelem = T.alloc_buffer((T.int64(1), T.int64(32), T.int64(1)))
        T_softmax_exp = T.alloc_buffer((T.int64(1), T.int64(32), T.int64(1), n))
        T_softmax_expsum = T.alloc_buffer((T.int64(1), T.int64(32), T.int64(1)))
        var_T_softmax_norm_intermediate = T.alloc_buffer((T.int64(1), T.int64(32), T.int64(1), n))
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(32), T.int64(1), n):
            with T.block("T_softmax_maxelem"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv94[v_i0, v_i1, v_i2, v_k])
                T.writes(T_softmax_maxelem[v_i0, v_i1, v_i2])
                with T.init():
                    T_softmax_maxelem[v_i0, v_i1, v_i2] = T.float32(-3.4028234663852886e+38)
                T_softmax_maxelem[v_i0, v_i1, v_i2] = T.max(T_softmax_maxelem[v_i0, v_i1, v_i2], lv94[v_i0, v_i1, v_i2, v_k])
        for i0, i1, i2, i3 in T.grid(T.int64(1), T.int64(32), T.int64(1), n):
            with T.block("T_softmax_exp"):
                v_i0, v_i1, v_i2, v_i3 = T.axis.remap("SSSS", [i0, i1, i2, i3])
                T.reads(lv94[v_i0, v_i1, v_i2, v_i3], T_softmax_maxelem[v_i0, v_i1, v_i2])
                T.writes(T_softmax_exp[v_i0, v_i1, v_i2, v_i3])
                T_softmax_exp[v_i0, v_i1, v_i2, v_i3] = T.exp(lv94[v_i0, v_i1, v_i2, v_i3] - T_softmax_maxelem[v_i0, v_i1, v_i2])
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(32), T.int64(1), n):
            with T.block("T_softmax_expsum"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(T_softmax_exp[v_i0, v_i1, v_i2, v_k])
                T.writes(T_softmax_expsum[v_i0, v_i1, v_i2])
                with T.init():
                    T_softmax_expsum[v_i0, v_i1, v_i2] = T.float32(0)
                T_softmax_expsum[v_i0, v_i1, v_i2] = T_softmax_expsum[v_i0, v_i1, v_i2] + T_softmax_exp[v_i0, v_i1, v_i2, v_k]
        for i0, i1, i2, i3 in T.grid(T.int64(1), T.int64(32), T.int64(1), n):
            with T.block("T_softmax_norm"):
                v_i0, v_i1, v_i2, v_i3 = T.axis.remap("SSSS", [i0, i1, i2, i3])
                T.reads(T_softmax_exp[v_i0, v_i1, v_i2, v_i3], T_softmax_expsum[v_i0, v_i1, v_i2])
                T.writes(var_T_softmax_norm_intermediate[v_i0, v_i1, v_i2, v_i3])
                T.block_attr({"axis": 3})
                var_T_softmax_norm_intermediate[v_i0, v_i1, v_i2, v_i3] = T_softmax_exp[v_i0, v_i1, v_i2, v_i3] / T_softmax_expsum[v_i0, v_i1, v_i2]
        for i0, i1, i2, i3 in T.grid(T.int64(1), T.int64(32), T.int64(1), n):
            with T.block("compute"):
                v_i0, v_i1, v_i2, v_i3 = T.axis.remap("SSSS", [i0, i1, i2, i3])
                T.reads(var_T_softmax_norm_intermediate[v_i0, v_i1, v_i2, v_i3])
                T.writes(var_compute_intermediate[v_i0, v_i1, v_i2, v_i3])
                var_compute_intermediate[v_i0, v_i1, v_i2, v_i3] = T.Cast("float16", var_T_softmax_norm_intermediate[v_i0, v_i1, v_i2, v_i3])

    @T.prim_func
    def fused_softmax2_cast4(p_lv36: T.handle, p_output0: T.handle):
        T.func_attr({"tir.noalias": T.bool(True)})
        n, m = T.int64(), T.int64()
        lv36 = T.match_buffer(p_lv36, (T.int64(1), T.int64(32), n, m))
        var_compute_intermediate = T.match_buffer(p_output0, (T.int64(1), T.int64(32), n, m), "float16")
        # with T.block("root"):
        T_softmax_maxelem = T.alloc_buffer((T.int64(1), T.int64(32), n))
        T_softmax_exp = T.alloc_buffer((T.int64(1), T.int64(32), n, m))
        T_softmax_expsum = T.alloc_buffer((T.int64(1), T.int64(32), n))
        var_T_softmax_norm_intermediate = T.alloc_buffer((T.int64(1), T.int64(32), n, m))
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(32), n, m):
            with T.block("T_softmax_maxelem"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(lv36[v_i0, v_i1, v_i2, v_k])
                T.writes(T_softmax_maxelem[v_i0, v_i1, v_i2])
                with T.init():
                    T_softmax_maxelem[v_i0, v_i1, v_i2] = T.float32(-3.4028234663852886e+38)
                T_softmax_maxelem[v_i0, v_i1, v_i2] = T.max(T_softmax_maxelem[v_i0, v_i1, v_i2], lv36[v_i0, v_i1, v_i2, v_k])
        for i0, i1, i2, i3 in T.grid(T.int64(1), T.int64(32), n, m):
            with T.block("T_softmax_exp"):
                v_i0, v_i1, v_i2, v_i3 = T.axis.remap("SSSS", [i0, i1, i2, i3])
                T.reads(lv36[v_i0, v_i1, v_i2, v_i3], T_softmax_maxelem[v_i0, v_i1, v_i2])
                T.writes(T_softmax_exp[v_i0, v_i1, v_i2, v_i3])
                T_softmax_exp[v_i0, v_i1, v_i2, v_i3] = T.exp(lv36[v_i0, v_i1, v_i2, v_i3] - T_softmax_maxelem[v_i0, v_i1, v_i2])
        for i0, i1, i2, k in T.grid(T.int64(1), T.int64(32), n, m):
            with T.block("T_softmax_expsum"):
                v_i0, v_i1, v_i2, v_k = T.axis.remap("SSSR", [i0, i1, i2, k])
                T.reads(T_softmax_exp[v_i0, v_i1, v_i2, v_k])
                T.writes(T_softmax_expsum[v_i0, v_i1, v_i2])
                with T.init():
                    T_softmax_expsum[v_i0, v_i1, v_i2] = T.float32(0)
                T_softmax_expsum[v_i0, v_i1, v_i2] = T_softmax_expsum[v_i0, v_i1, v_i2] + T_softmax_exp[v_i0, v_i1, v_i2, v_k]
        for i0, i1, i2, i3 in T.grid(T.int64(1), T.int64(32), n, m):
            with T.block("T_softmax_norm"):
                v_i0, v_i1, v_i2, v_i3 = T.axis.remap("SSSS", [i0, i1, i2, i3])
                T.reads(T_softmax_exp[v_i0, v_i1, v_i2, v_i3], T_softmax_expsum[v_i0, v_i1, v_i2])
                T.writes(var_T_softmax_norm_intermediate[v_i0, v_i1, v_i2, v_i3])
                T.block_attr({"axis": 3})
                var_T_softmax_norm_intermediate[v_i0, v_i1, v_i2, v_i3] = T_softmax_exp[v_i0, v_i1, v_i2, v_i3] / T_softmax_expsum[v_i0, v_i1, v_i2]
        for i0, i1, i2, i3 in T.grid(T.int64(1), T.int64(32), n, m):
            with T.block("compute"):
                v_i0, v_i1, v_i2, v_i3 = T.axis.remap("SSSS", [i0, i1, i2, i3])
                T.reads(var_T_softmax_norm_intermediate[v_i0, v_i1, v_i2, v_i3])
                T.writes(var_compute_intermediate[v_i0, v_i1, v_i2, v_i3])
                var_compute_intermediate[v_i0, v_i1, v_i2, v_i3] = T.Cast("float16", var_T_softmax_norm_intermediate[v_i0, v_i1, v_i2, v_i3])

    @T.prim_func
    def fused_transpose3_reshape4(lv97: T.Buffer((T.int64(1), T.int64(32), T.int64(1), T.int64(128)), "float16"), var_T_reshape_intermediate: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")):
        T.func_attr({"tir.noalias": T.bool(True)})
        # with T.block("root"):
        var_T_transpose_intermediate = T.alloc_buffer((T.int64(1), T.int64(1), T.int64(32), T.int64(128)), "float16")
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), T.int64(1), T.int64(32), T.int64(128)):
            with T.block("T_transpose"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(lv97[v_ax0, v_ax2, v_ax1, v_ax3])
                T.writes(var_T_transpose_intermediate[v_ax0, v_ax1, v_ax2, v_ax3])
                var_T_transpose_intermediate[v_ax0, v_ax1, v_ax2, v_ax3] = lv97[v_ax0, v_ax2, v_ax1, v_ax3]
        for ax0, ax1, ax2 in T.grid(T.int64(1), T.int64(1), T.int64(4096)):
            with T.block("T_reshape"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(var_T_transpose_intermediate[T.int64(0), T.int64(0), v_ax2 % T.int64(4096) // T.int64(128), v_ax2 % T.int64(128)])
                T.writes(var_T_reshape_intermediate[v_ax0, v_ax1, v_ax2])
                var_T_reshape_intermediate[v_ax0, v_ax1, v_ax2] = var_T_transpose_intermediate[T.int64(0), T.int64(0), v_ax2 % T.int64(4096) // T.int64(128), v_ax2 % T.int64(128)]

    @T.prim_func
    def matmul2(var_A: T.handle, var_B: T.handle, matmul: T.Buffer((T.int64(1), T.int64(32), T.int64(1), T.int64(128)), "float16")):
        T.func_attr({"op_pattern": 4, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (T.int64(1), T.int64(32), T.int64(1), n), "float16")
        B = T.match_buffer(var_B, (T.int64(1), T.int64(32), n, T.int64(128)), "float16")
        # with T.block("root"):
        for i0, i1, i2, i3, k in T.grid(T.int64(1), T.int64(32), T.int64(1), T.int64(128), n):
            with T.block("matmul"):
                v_i0, v_i1, v_i2, v_i3, v_k = T.axis.remap("SSSSR", [i0, i1, i2, i3, k])
                T.reads(A[v_i0, v_i1, v_i2, v_k], B[v_i0, v_i1, v_k, v_i3])
                T.writes(matmul[v_i0, v_i1, v_i2, v_i3])
                with T.init():
                    matmul[v_i0, v_i1, v_i2, v_i3] = T.float16(0)
                matmul[v_i0, v_i1, v_i2, v_i3] = matmul[v_i0, v_i1, v_i2, v_i3] + A[v_i0, v_i1, v_i2, v_k] * B[v_i0, v_i1, v_k, v_i3]

    @T.prim_func
    def matmul8(var_A: T.handle, var_B: T.handle, var_matmul: T.handle):
        T.func_attr({"op_pattern": 4, "tir.noalias": T.bool(True)})
        n, m = T.int64(), T.int64()
        A = T.match_buffer(var_A, (T.int64(1), T.int64(32), n, m), "float16")
        B = T.match_buffer(var_B, (T.int64(1), T.int64(32), m, T.int64(128)), "float16")
        matmul = T.match_buffer(var_matmul, (T.int64(1), T.int64(32), n, T.int64(128)), "float16")
        # with T.block("root"):
        for i0, i1, i2, i3, k in T.grid(T.int64(1), T.int64(32), n, T.int64(128), m):
            with T.block("matmul"):
                v_i0, v_i1, v_i2, v_i3, v_k = T.axis.remap("SSSSR", [i0, i1, i2, i3, k])
                T.reads(A[v_i0, v_i1, v_i2, v_k], B[v_i0, v_i1, v_k, v_i3])
                T.writes(matmul[v_i0, v_i1, v_i2, v_i3])
                with T.init():
                    matmul[v_i0, v_i1, v_i2, v_i3] = T.float16(0)
                matmul[v_i0, v_i1, v_i2, v_i3] = matmul[v_i0, v_i1, v_i2, v_i3] + A[v_i0, v_i1, v_i2, v_k] * B[v_i0, v_i1, v_k, v_i3]

    @T.prim_func
    def reshape(A: T.Buffer((T.int64(1), T.int64(1)), "int32"), T_reshape: T.Buffer((T.int64(1),), "int32")):
        T.func_attr({"op_pattern": 1, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        for ax0 in range(T.int64(1)):
            with T.block("T_reshape"):
                v_ax0 = T.axis.spatial(T.int64(1), ax0)
                T.reads(A[T.int64(0), T.int64(0)])
                T.writes(T_reshape[v_ax0])
                T_reshape[v_ax0] = A[T.int64(0), T.int64(0)]

    @T.prim_func
    def reshape1(A: T.Buffer((T.int64(1), T.int64(4096)), "float16"), T_reshape: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")):
        T.func_attr({"op_pattern": 2, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        for ax0, ax1, ax2 in T.grid(T.int64(1), T.int64(1), T.int64(4096)):
            with T.block("T_reshape"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(A[T.int64(0), v_ax2 % T.int64(4096)])
                T.writes(T_reshape[v_ax0, v_ax1, v_ax2])
                T_reshape[v_ax0, v_ax1, v_ax2] = A[T.int64(0), v_ax2 % T.int64(4096)]

    @T.prim_func
    def reshape2(A: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), T_reshape: T.Buffer((T.int64(1), T.int64(1), T.int64(32), T.int64(128)), "float16")):
        T.func_attr({"op_pattern": 2, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), T.int64(1), T.int64(32), T.int64(128)):
            with T.block("T_reshape"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(A[T.int64(0), T.int64(0), (v_ax2 * T.int64(128) + v_ax3) % T.int64(4096)])
                T.writes(T_reshape[v_ax0, v_ax1, v_ax2, v_ax3])
                T_reshape[v_ax0, v_ax1, v_ax2, v_ax3] = A[T.int64(0), T.int64(0), (v_ax2 * T.int64(128) + v_ax3) % T.int64(4096)]

    @T.prim_func
    def reshape3(var_A: T.handle, var_T_reshape: T.handle):
        T.func_attr({"op_pattern": 8, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (n, T.int64(32), T.int64(128)), "float16")
        T_reshape = T.match_buffer(var_T_reshape, (T.int64(1), n, T.int64(32), T.int64(128)), "float16")
        # with T.block("root"):
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), n, T.int64(32), T.int64(128)):
            with T.block("T_reshape"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(A[((v_ax3 // T.int64(128) + v_ax2) // T.int64(32) + v_ax0 * n + v_ax1) % n, (v_ax3 // T.int64(128) + v_ax2) % T.int64(32), v_ax3 % T.int64(128)])
                T.writes(T_reshape[v_ax0, v_ax1, v_ax2, v_ax3])
                T_reshape[v_ax0, v_ax1, v_ax2, v_ax3] = A[((v_ax3 // T.int64(128) + v_ax2) // T.int64(32) + v_ax0 * n + v_ax1) % n, (v_ax3 // T.int64(128) + v_ax2) % T.int64(32), v_ax3 % T.int64(128)]

    @T.prim_func
    def reshape5(var_A: T.handle, var_T_reshape: T.handle):
        T.func_attr({"op_pattern": 8, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (T.int64(1), n), "int32")
        T_reshape = T.match_buffer(var_T_reshape, (n,), "int32")
        # with T.block("root"):
        for ax0 in range(n):
            with T.block("T_reshape"):
                v_ax0 = T.axis.spatial(n, ax0)
                T.reads(A[T.int64(0), v_ax0 % n])
                T.writes(T_reshape[v_ax0])
                T_reshape[v_ax0] = A[T.int64(0), v_ax0 % n]

    @T.prim_func
    def reshape6(var_A: T.handle, var_T_reshape: T.handle):
        T.func_attr({"op_pattern": 8, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (n, T.int64(4096)), "float16")
        T_reshape = T.match_buffer(var_T_reshape, (T.int64(1), n, T.int64(4096)), "float16")
        # with T.block("root"):
        for ax0, ax1, ax2 in T.grid(T.int64(1), n, T.int64(4096)):
            with T.block("T_reshape"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(A[(v_ax2 // T.int64(4096) + v_ax0 * n + v_ax1) % n, v_ax2 % T.int64(4096)])
                T.writes(T_reshape[v_ax0, v_ax1, v_ax2])
                T_reshape[v_ax0, v_ax1, v_ax2] = A[(v_ax2 // T.int64(4096) + v_ax0 * n + v_ax1) % n, v_ax2 % T.int64(4096)]

    @T.prim_func
    def reshape7(var_A: T.handle, var_T_reshape: T.handle):
        T.func_attr({"op_pattern": 8, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (T.int64(1), n, T.int64(4096)), "float16")
        T_reshape = T.match_buffer(var_T_reshape, (T.int64(1), n, T.int64(32), T.int64(128)), "float16")
        # with T.block("root"):
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), n, T.int64(32), T.int64(128)):
            with T.block("T_reshape"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(A[T.int64(0), ((v_ax2 * T.int64(128) + v_ax3) // T.int64(4096) + v_ax0 * n + v_ax1) % n, (v_ax2 * T.int64(128) + v_ax3) % T.int64(4096)])
                T.writes(T_reshape[v_ax0, v_ax1, v_ax2, v_ax3])
                T_reshape[v_ax0, v_ax1, v_ax2, v_ax3] = A[T.int64(0), ((v_ax2 * T.int64(128) + v_ax3) // T.int64(4096) + v_ax0 * n + v_ax1) % n, (v_ax2 * T.int64(128) + v_ax3) % T.int64(4096)]

    @T.prim_func
    def reshape8(var_A: T.handle, var_T_reshape: T.handle):
        T.func_attr({"op_pattern": 8, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (T.int64(1), n, T.int64(32), T.int64(128)), "float16")
        T_reshape = T.match_buffer(var_T_reshape, (T.int64(1), n, T.int64(4096)), "float16")
        # with T.block("root"):
        for ax0, ax1, ax2 in T.grid(T.int64(1), n, T.int64(4096)):
            with T.block("T_reshape"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(A[T.int64(0), (v_ax2 // T.int64(4096) + v_ax0 * n + v_ax1) % n, v_ax2 % T.int64(4096) // T.int64(128), v_ax2 % T.int64(128)])
                T.writes(T_reshape[v_ax0, v_ax1, v_ax2])
                T_reshape[v_ax0, v_ax1, v_ax2] = A[T.int64(0), (v_ax2 // T.int64(4096) + v_ax0 * n + v_ax1) % n, v_ax2 % T.int64(4096) // T.int64(128), v_ax2 % T.int64(128)]

    @T.prim_func
    def rms_norm(var_A: T.handle, B: T.Buffer((T.int64(4096),), "float16"), var_rms_norm: T.handle):
        T.func_attr({"op_pattern": 4, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (T.int64(1), n, T.int64(4096)), "float16")
        rms_norm_1 = T.match_buffer(var_rms_norm, (T.int64(1), n, T.int64(4096)), "float16")
        # with T.block("root"):
        Ared_temp = T.alloc_buffer((T.int64(1), n))
        for bsz, i, k in T.grid(T.int64(1), n, T.int64(4096)):
            with T.block("Ared_temp"):
                v_bsz, v_i, v_k = T.axis.remap("SSR", [bsz, i, k])
                T.reads(A[v_bsz, v_i, v_k])
                T.writes(Ared_temp[v_bsz, v_i])
                with T.init():
                    Ared_temp[v_bsz, v_i] = T.float32(0)
                Ared_temp[v_bsz, v_i] = Ared_temp[v_bsz, v_i] + T.Cast("float32", A[v_bsz, v_i, v_k]) * T.Cast("float32", A[v_bsz, v_i, v_k])
        for bsz, i, k in T.grid(T.int64(1), n, T.int64(4096)):
            with T.block("rms_norm"):
                v_bsz, v_i, v_k = T.axis.remap("SSS", [bsz, i, k])
                T.reads(B[v_k], A[v_bsz, v_i, v_k], Ared_temp[v_bsz, v_i])
                T.writes(rms_norm_1[v_bsz, v_i, v_k])
                rms_norm_1[v_bsz, v_i, v_k] = T.Cast("float16", T.Cast("float32", B[v_k]) * (T.Cast("float32", A[v_bsz, v_i, v_k]) / T.sqrt(Ared_temp[v_bsz, v_i] * T.float32(0.000244140625) + T.float32(9.9999999999999995e-07))))

    @T.prim_func
    def rms_norm1(A: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), B: T.Buffer((T.int64(4096),), "float16"), rms_norm: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")):
        T.func_attr({"op_pattern": 4, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        Ared_temp = T.alloc_buffer((T.int64(1), T.int64(1)))
        for bsz, i, k in T.grid(T.int64(1), T.int64(1), T.int64(4096)):
            with T.block("Ared_temp"):
                v_bsz, v_i, v_k = T.axis.remap("SSR", [bsz, i, k])
                T.reads(A[v_bsz, v_i, v_k])
                T.writes(Ared_temp[v_bsz, v_i])
                with T.init():
                    Ared_temp[v_bsz, v_i] = T.float32(0)
                Ared_temp[v_bsz, v_i] = Ared_temp[v_bsz, v_i] + T.Cast("float32", A[v_bsz, v_i, v_k]) * T.Cast("float32", A[v_bsz, v_i, v_k])
        for bsz, i, k in T.grid(T.int64(1), T.int64(1), T.int64(4096)):
            with T.block("rms_norm"):
                v_bsz, v_i, v_k = T.axis.remap("SSS", [bsz, i, k])
                T.reads(B[v_k], A[v_bsz, v_i, v_k], Ared_temp[v_bsz, v_i])
                T.writes(rms_norm[v_bsz, v_i, v_k])
                rms_norm[v_bsz, v_i, v_k] = T.Cast("float16", T.Cast("float32", B[v_k]) * (T.Cast("float32", A[v_bsz, v_i, v_k]) / T.sqrt(Ared_temp[v_bsz, v_i] * T.float32(0.000244140625) + T.float32(9.9999999999999995e-07))))

    @T.prim_func
    def rotary_embedding(var_A: T.handle, B: T.Buffer((T.int64(2048), T.int64(128)), "float16"), C: T.Buffer((T.int64(2048), T.int64(128)), "float16"), var_rotary: T.handle, m: T.int64):
        T.func_attr({"op_pattern": 8, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (T.int64(1), n, T.int64(32), T.int64(128)), "float16")
        rotary = T.match_buffer(var_rotary, (T.int64(1), n, T.int64(32), T.int64(128)), "float16")
        # with T.block("root"):
        for i0, i1, i2, i3 in T.grid(T.int64(1), n, T.int64(32), T.int64(128)):
            with T.block("rotary"):
                v_i0, v_i1, v_i2, v_i3 = T.axis.remap("SSSS", [i0, i1, i2, i3])
                T.reads(B[m + v_i1 - n, v_i3], A[v_i0, v_i1, v_i2, v_i3 - T.int64(64):v_i3 - T.int64(64) + T.int64(129)], C[m + v_i1 - n, v_i3])
                T.writes(rotary[v_i0, v_i1, v_i2, v_i3])
                rotary[v_i0, v_i1, v_i2, v_i3] = B[m + v_i1 - n, v_i3] * A[v_i0, v_i1, v_i2, v_i3] + C[m + v_i1 - n, v_i3] * T.Select(T.int64(64) <= v_i3, A[v_i0, v_i1, v_i2, v_i3 - T.int64(64)], A[v_i0, v_i1, v_i2, v_i3 + T.int64(64)] * T.float16(-1))

    @T.prim_func
    def rotary_embedding1(A: T.Buffer((T.int64(1), T.int64(1), T.int64(32), T.int64(128)), "float16"), B: T.Buffer((T.int64(2048), T.int64(128)), "float16"), C: T.Buffer((T.int64(2048), T.int64(128)), "float16"), rotary: T.Buffer((T.int64(1), T.int64(1), T.int64(32), T.int64(128)), "float16"), n: T.int64):
        T.func_attr({"op_pattern": 8, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        for i0, i1, i2, i3 in T.grid(T.int64(1), T.int64(1), T.int64(32), T.int64(128)):
            with T.block("rotary"):
                v_i0, v_i1, v_i2, v_i3 = T.axis.remap("SSSS", [i0, i1, i2, i3])
                T.reads(B[n + v_i1 - T.int64(1), v_i3], A[v_i0, v_i1, v_i2, v_i3 - T.int64(64):v_i3 - T.int64(64) + T.int64(129)], C[n + v_i1 - T.int64(1), v_i3])
                T.writes(rotary[v_i0, v_i1, v_i2, v_i3])
                rotary[v_i0, v_i1, v_i2, v_i3] = B[n + v_i1 - T.int64(1), v_i3] * A[v_i0, v_i1, v_i2, v_i3] + C[n + v_i1 - T.int64(1), v_i3] * T.Select(T.int64(64) <= v_i3, A[v_i0, v_i1, v_i2, v_i3 - T.int64(64)], A[v_i0, v_i1, v_i2, v_i3 + T.int64(64)] * T.float16(-1))

    @T.prim_func
    def slice(var_A: T.handle, slice_1: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")):
        T.func_attr({"op_pattern": 8, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (T.int64(1), n, T.int64(4096)), "float16")
        # with T.block("root"):
        for i, j, k in T.grid(T.int64(1), T.int64(1), T.int64(4096)):
            with T.block("slice"):
                v_i, v_j, v_k = T.axis.remap("SSS", [i, j, k])
                T.reads(A[v_i, n - T.int64(1), v_k])
                T.writes(slice_1[v_i, v_j, v_k])
                slice_1[v_i, v_j, v_k] = A[v_i, n - T.int64(1), v_k]

    @T.prim_func
    def slice1(A: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16"), slice: T.Buffer((T.int64(1), T.int64(1), T.int64(4096)), "float16")):
        T.func_attr({"op_pattern": 1, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        for i, j, k in T.grid(T.int64(1), T.int64(1), T.int64(4096)):
            with T.block("slice"):
                v_i, v_j, v_k = T.axis.remap("SSS", [i, j, k])
                T.reads(A[v_i, T.int64(0), v_k])
                T.writes(slice[v_i, v_j, v_k])
                slice[v_i, v_j, v_k] = A[v_i, T.int64(0), v_k]

    @T.prim_func
    def softmax(A: T.Buffer((T.int64(1), T.int64(1), T.int64(32000)), "float32"), T_softmax_norm: T.Buffer((T.int64(1), T.int64(1), T.int64(32000)), "float32")):
        T.func_attr({"op_pattern": 4, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        T_softmax_maxelem = T.alloc_buffer((T.int64(1), T.int64(1)))
        T_softmax_exp = T.alloc_buffer((T.int64(1), T.int64(1), T.int64(32000)))
        T_softmax_expsum = T.alloc_buffer((T.int64(1), T.int64(1)))
        for i0, i1, k in T.grid(T.int64(1), T.int64(1), T.int64(32000)):
            with T.block("T_softmax_maxelem"):
                v_i0, v_i1, v_k = T.axis.remap("SSR", [i0, i1, k])
                T.reads(A[v_i0, v_i1, v_k])
                T.writes(T_softmax_maxelem[v_i0, v_i1])
                with T.init():
                    T_softmax_maxelem[v_i0, v_i1] = T.float32(-3.4028234663852886e+38)
                T_softmax_maxelem[v_i0, v_i1] = T.max(T_softmax_maxelem[v_i0, v_i1], A[v_i0, v_i1, v_k])
        for i0, i1, i2 in T.grid(T.int64(1), T.int64(1), T.int64(32000)):
            with T.block("T_softmax_exp"):
                v_i0, v_i1, v_i2 = T.axis.remap("SSS", [i0, i1, i2])
                T.reads(A[v_i0, v_i1, v_i2], T_softmax_maxelem[v_i0, v_i1])
                T.writes(T_softmax_exp[v_i0, v_i1, v_i2])
                T_softmax_exp[v_i0, v_i1, v_i2] = T.exp(A[v_i0, v_i1, v_i2] - T_softmax_maxelem[v_i0, v_i1])
        for i0, i1, k in T.grid(T.int64(1), T.int64(1), T.int64(32000)):
            with T.block("T_softmax_expsum"):
                v_i0, v_i1, v_k = T.axis.remap("SSR", [i0, i1, k])
                T.reads(T_softmax_exp[v_i0, v_i1, v_k])
                T.writes(T_softmax_expsum[v_i0, v_i1])
                with T.init():
                    T_softmax_expsum[v_i0, v_i1] = T.float32(0)
                T_softmax_expsum[v_i0, v_i1] = T_softmax_expsum[v_i0, v_i1] + T_softmax_exp[v_i0, v_i1, v_k]
        for i0, i1, i2 in T.grid(T.int64(1), T.int64(1), T.int64(32000)):
            with T.block("T_softmax_norm"):
                v_i0, v_i1, v_i2 = T.axis.remap("SSS", [i0, i1, i2])
                T.reads(T_softmax_exp[v_i0, v_i1, v_i2], T_softmax_expsum[v_i0, v_i1])
                T.writes(T_softmax_norm[v_i0, v_i1, v_i2])
                T.block_attr({"axis": 2})
                T_softmax_norm[v_i0, v_i1, v_i2] = T_softmax_exp[v_i0, v_i1, v_i2] / T_softmax_expsum[v_i0, v_i1]

    @T.prim_func
    def squeeze(A: T.Buffer((T.int64(1), T.int64(1), T.int64(32), T.int64(128)), "float16"), T_squeeze: T.Buffer((T.int64(1), T.int64(32), T.int64(128)), "float16")):
        T.func_attr({"op_pattern": 1, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        for ax0, ax1, ax2 in T.grid(T.int64(1), T.int64(32), T.int64(128)):
            with T.block("T_squeeze"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(A[T.int64(0), v_ax0, v_ax1, v_ax2])
                T.writes(T_squeeze[v_ax0, v_ax1, v_ax2])
                T_squeeze[v_ax0, v_ax1, v_ax2] = A[T.int64(0), v_ax0, v_ax1, v_ax2]

    @T.prim_func
    def squeeze1(var_A: T.handle, var_T_squeeze: T.handle):
        T.func_attr({"op_pattern": 1, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (T.int64(1), n, T.int64(32), T.int64(128)), "float16")
        T_squeeze = T.match_buffer(var_T_squeeze, (n, T.int64(32), T.int64(128)), "float16")
        # with T.block("root"):
        for ax0, ax1, ax2 in T.grid(n, T.int64(32), T.int64(128)):
            with T.block("T_squeeze"):
                v_ax0, v_ax1, v_ax2 = T.axis.remap("SSS", [ax0, ax1, ax2])
                T.reads(A[T.int64(0), v_ax0, v_ax1, v_ax2])
                T.writes(T_squeeze[v_ax0, v_ax1, v_ax2])
                T_squeeze[v_ax0, v_ax1, v_ax2] = A[T.int64(0), v_ax0, v_ax1, v_ax2]

    @T.prim_func
    def take_decode(A: T.Buffer((T.int64(32000), T.int64(512)), "uint32"), B: T.Buffer((T.int64(32000), T.int64(128)), "float16"), C: T.Buffer((T.int64(1),), "int32"), take_decode_1: T.Buffer((T.int64(1), T.int64(4096)), "float16")):
        T.func_attr({"op_pattern": 8, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        for i, j in T.grid(T.int64(1), T.int64(4096)):
            with T.block("take_decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(A[C[v_i], v_j // T.int64(8)], C[v_i], B[C[v_i], v_j // T.int64(32)])
                T.writes(take_decode_1[v_i, v_j])
                take_decode_1[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(A[C[v_i], v_j // T.int64(8)], T.Cast("uint32", v_j % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * B[C[v_i], v_j // T.int64(32)]

    @T.prim_func
    def take_decode1(A: T.Buffer((T.int64(32000), T.int64(512)), "uint32"), B: T.Buffer((T.int64(32000), T.int64(128)), "float16"), var_C: T.handle, var_take_decode: T.handle):
        T.func_attr({"op_pattern": 8, "tir.noalias": T.bool(True)})
        n = T.int64()
        C = T.match_buffer(var_C, (n,), "int32")
        take_decode = T.match_buffer(var_take_decode, (n, T.int64(4096)), "float16")
        # with T.block("root"):
        for i, j in T.grid(n, T.int64(4096)):
            with T.block("take_decode"):
                v_i, v_j = T.axis.remap("SS", [i, j])
                T.reads(A[C[v_i], v_j // T.int64(8)], C[v_i], B[C[v_i], v_j // T.int64(32)])
                T.writes(take_decode[v_i, v_j])
                take_decode[v_i, v_j] = (T.Cast("float16", T.bitwise_and(T.shift_right(A[C[v_i], v_j // T.int64(8)], T.Cast("uint32", v_j % T.int64(8)) * T.uint32(4)), T.uint32(15))) - T.float16(7)) * B[C[v_i], v_j // T.int64(32)]

    @T.prim_func
    def transpose1(A: T.Buffer((T.int64(1), T.int64(1), T.int64(32), T.int64(128)), "float16"), T_transpose: T.Buffer((T.int64(1), T.int64(32), T.int64(1), T.int64(128)), "float16")):
        T.func_attr({"op_pattern": 2, "tir.noalias": T.bool(True)})
        # with T.block("root"):
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), T.int64(32), T.int64(1), T.int64(128)):
            with T.block("T_transpose"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(A[v_ax0, v_ax2, v_ax1, v_ax3])
                T.writes(T_transpose[v_ax0, v_ax1, v_ax2, v_ax3])
                T_transpose[v_ax0, v_ax1, v_ax2, v_ax3] = A[v_ax0, v_ax2, v_ax1, v_ax3]

    @T.prim_func
    def transpose2(var_A: T.handle, var_T_transpose: T.handle):
        T.func_attr({"op_pattern": 2, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (T.int64(1), n, T.int64(32), T.int64(128)), "float16")
        T_transpose = T.match_buffer(var_T_transpose, (T.int64(1), T.int64(32), n, T.int64(128)), "float16")
        # with T.block("root"):
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), T.int64(32), n, T.int64(128)):
            with T.block("T_transpose"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(A[v_ax0, v_ax2, v_ax1, v_ax3])
                T.writes(T_transpose[v_ax0, v_ax1, v_ax2, v_ax3])
                T_transpose[v_ax0, v_ax1, v_ax2, v_ax3] = A[v_ax0, v_ax2, v_ax1, v_ax3]

    @T.prim_func
    def transpose6(var_A: T.handle, var_T_transpose: T.handle):
        T.func_attr({"op_pattern": 2, "tir.noalias": T.bool(True)})
        n = T.int64()
        A = T.match_buffer(var_A, (T.int64(1), T.int64(32), n, T.int64(128)), "float16")
        T_transpose = T.match_buffer(var_T_transpose, (T.int64(1), n, T.int64(32), T.int64(128)), "float16")
        # with T.block("root"):
        for ax0, ax1, ax2, ax3 in T.grid(T.int64(1), n, T.int64(32), T.int64(128)):
            with T.block("T_transpose"):
                v_ax0, v_ax1, v_ax2, v_ax3 = T.axis.remap("SSSS", [ax0, ax1, ax2, ax3])
                T.reads(A[v_ax0, v_ax2, v_ax1, v_ax3])
                T.writes(T_transpose[v_ax0, v_ax1, v_ax2, v_ax3])
                T_transpose[v_ax0, v_ax1, v_ax2, v_ax3] = A[v_ax0, v_ax2, v_ax1, v_ax3]

    @R.function
    def create_kv_cache() -> R.Tuple(R.Object, R.Object):
        R.func_attr({"tir_var_upper_bound": {"m": 2048, "n": 2048}})
        with R.dataflow():
            lv119: R.Object = R.call_packed("vm.builtin.attention_kv_cache_create", metadata["relax.expr.Constant"][0], R.shape([2048, 32, 128]), R.prim_value(0), sinfo_args=(R.Object,))
            lv120: R.Object = R.call_packed("vm.builtin.attention_kv_cache_create", metadata["relax.expr.Constant"][0], R.shape([2048, 32, 128]), R.prim_value(0), sinfo_args=(R.Object,))
            gv2: R.Tuple(R.Object, R.Object) = lv119, lv120
            R.output(gv2)
        return gv2

    @R.function
    def decoding(input_ids1: R.Tensor((1, 1), dtype="int32"), all_seq_len: R.Shape(["n"]), kv_cache: R.Tuple(R.Object, R.Object), params: R.Tuple(R.Tensor((4096,), dtype="float16"), R.Tensor((4096,), dtype="float16"), R.Tensor((4096,), dtype="float16"), R.Tensor((2048, 128), dtype="float16"), R.Tensor((2048, 128), dtype="float16"), R.Tensor((32000, 512), dtype="uint32"), R.Tensor((32000, 128), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 11008), dtype="uint32"), R.Tensor((128, 11008), dtype="float16"), R.Tensor((512, 11008), dtype="uint32"), R.Tensor((128, 11008), dtype="float16"), R.Tensor((1376, 4096), dtype="uint32"), R.Tensor((344, 4096), dtype="float16"), R.Tensor((512, 32000), dtype="uint32"), R.Tensor((128, 32000), dtype="float16"))) -> R.Tuple(R.Tensor((1, 1, 32000), dtype="float32"), R.Tuple(R.Object, R.Object)):
        n = T.int64()
        R.func_attr({"tir_var_upper_bound": {"m": 2048, "n": 2048}})
        cls = Module
        with R.dataflow():
            lv60 = R.call_tir(cls.reshape, (input_ids1,), out_sinfo=R.Tensor((1,), dtype="int32"))
            lv25: R.Tensor((32000, 512), dtype="uint32") = params[5]
            lv26: R.Tensor((32000, 128), dtype="float16") = params[6]
            lv61 = R.call_tir(cls.take_decode, (lv25, lv26, lv60), out_sinfo=R.Tensor((1, 4096), dtype="float16"))
            lv62 = R.call_tir(cls.reshape1, (lv61,), out_sinfo=R.Tensor((1, 1, 4096), dtype="float16"))
            lv27: R.Tensor((4096,), dtype="float16") = params[0]
            lv64 = R.call_tir(cls.rms_norm1, (lv62, lv27), out_sinfo=R.Tensor((1, 1, 4096), dtype="float16"))
            lv28: R.Tensor((512, 4096), dtype="uint32") = params[7]
            lv29: R.Tensor((128, 4096), dtype="float16") = params[8]
            lv1 = R.call_tir(cls.fused_decode_matmul1, (lv28, lv29, lv64), out_sinfo=R.Tensor((1, 1, 4096), dtype="float16"))
            lv67 = R.call_tir(cls.reshape2, (lv1,), out_sinfo=R.Tensor((1, 1, 32, 128), dtype="float16"))
            lv30: R.Tensor((2048, 128), dtype="float16") = params[3]
            lv31: R.Tensor((2048, 128), dtype="float16") = params[4]
            lv74 = R.call_tir(cls.rotary_embedding1, (lv67, lv30, lv31), out_sinfo=R.Tensor((1, 1, 32, 128), dtype="float16"), tir_vars=R.shape([n]))
            lv86 = R.call_tir(cls.transpose1, (lv74,), out_sinfo=R.Tensor((1, 32, 1, 128), dtype="float16"))
            lv78: R.Object = kv_cache[0]
            lv32: R.Tensor((512, 4096), dtype="uint32") = params[9]
            lv33: R.Tensor((128, 4096), dtype="float16") = params[10]
            lv2 = R.call_tir(cls.fused_decode_matmul1, (lv32, lv33, lv64), out_sinfo=R.Tensor((1, 1, 4096), dtype="float16"))
            lv70 = R.call_tir(cls.reshape2, (lv2,), out_sinfo=R.Tensor((1, 1, 32, 128), dtype="float16"))
            lv34: R.Tensor((2048, 128), dtype="float16") = params[3]
            lv35: R.Tensor((2048, 128), dtype="float16") = params[4]
            lv75 = R.call_tir(cls.rotary_embedding1, (lv70, lv34, lv35), out_sinfo=R.Tensor((1, 1, 32, 128), dtype="float16"), tir_vars=R.shape([n]))
            lv76 = R.call_tir(cls.squeeze, (lv75,), out_sinfo=R.Tensor((1, 32, 128), dtype="float16"))
            lv79: R.Object = R.call_packed("vm.builtin.attention_kv_cache_append", lv78, lv76, sinfo_args=(R.Object,))
            lv82: R.Tensor((n, 32, 128), dtype="float16") = R.call_packed("vm.builtin.attention_kv_cache_view", lv79, R.shape([n, 32, 128]), sinfo_args=(R.Tensor((n, 32, 128), dtype="float16"),))
            lv84 = R.call_tir(cls.reshape3, (lv82,), out_sinfo=R.Tensor((1, n, 32, 128), dtype="float16"))
            lv87 = R.call_tir(cls.transpose2, (lv84,), out_sinfo=R.Tensor((1, 32, n, 128), dtype="float16"))
            lv = R.call_tir(cls.fused_full_NT_matmul_divide1_maximum_minimum_cast, (lv86, lv87), out_sinfo=R.Tensor((1, 32, 1, n), dtype="float32"))
            lv36: R.Tensor((512, 4096), dtype="uint32") = params[11]
            lv37: R.Tensor((128, 4096), dtype="float16") = params[12]
            lv3 = R.call_tir(cls.fused_decode_matmul1, (lv36, lv37, lv64), out_sinfo=R.Tensor((1, 1, 4096), dtype="float16"))
            lv1_1 = R.call_tir(cls.fused_reshape2_squeeze, (lv3,), out_sinfo=R.Tensor((1, 32, 128), dtype="float16"))
            lv80: R.Object = kv_cache[1]
            lv81: R.Object = R.call_packed("vm.builtin.attention_kv_cache_append", lv80, lv1_1, sinfo_args=(R.Object,))
            lv83: R.Tensor((n, 32, 128), dtype="float16") = R.call_packed("vm.builtin.attention_kv_cache_view", lv81, R.shape([n, 32, 128]), sinfo_args=(R.Tensor((n, 32, 128), dtype="float16"),))
            lv85 = R.call_tir(cls.reshape3, (lv83,), out_sinfo=R.Tensor((1, n, 32, 128), dtype="float16"))
            lv88 = R.call_tir(cls.transpose2, (lv85,), out_sinfo=R.Tensor((1, 32, n, 128), dtype="float16"))
            lv2_1 = R.call_tir(cls.fused_softmax1_cast1, (lv,), out_sinfo=R.Tensor((1, 32, 1, n), dtype="float16"))
            lv97 = R.call_tir(cls.matmul2, (lv2_1, lv88), out_sinfo=R.Tensor((1, 32, 1, 128), dtype="float16"))
            lv3_1 = R.call_tir(cls.fused_transpose3_reshape4, (lv97,), out_sinfo=R.Tensor((1, 1, 4096), dtype="float16"))
            lv38: R.Tensor((512, 4096), dtype="uint32") = params[13]
            lv39: R.Tensor((128, 4096), dtype="float16") = params[14]
            lv_1 = R.call_tir(cls.fused_decode_fused_matmul1_add, (lv38, lv39, lv3_1, lv62), out_sinfo=R.Tensor((1, 1, 4096), dtype="float16"))
            lv40: R.Tensor((4096,), dtype="float16") = params[1]
            lv103 = R.call_tir(cls.rms_norm1, (lv_1, lv40), out_sinfo=R.Tensor((1, 1, 4096), dtype="float16"))
            lv41: R.Tensor((512, 11008), dtype="uint32") = params[15]
            lv42: R.Tensor((128, 11008), dtype="float16") = params[16]
            lv4 = R.call_tir(cls.fused_decode1_fused_matmul3_silu, (lv41, lv42, lv103), out_sinfo=R.Tensor((1, 1, 11008), dtype="float16"))
            lv43: R.Tensor((512, 11008), dtype="uint32") = params[17]
            lv44: R.Tensor((128, 11008), dtype="float16") = params[18]
            lv1_2 = R.call_tir(cls.fused_decode1_fused_matmul3_multiply, (lv43, lv44, lv103, lv4), out_sinfo=R.Tensor((1, 1, 11008), dtype="float16"))
            lv45: R.Tensor((1376, 4096), dtype="uint32") = params[19]
            lv46: R.Tensor((344, 4096), dtype="float16") = params[20]
            lv2_2 = R.call_tir(cls.fused_decode2_fused_matmul4_add, (lv45, lv46, lv1_2, lv_1), out_sinfo=R.Tensor((1, 1, 4096), dtype="float16"))
            lv47: R.Tensor((4096,), dtype="float16") = params[2]
            lv113 = R.call_tir(cls.rms_norm1, (lv2_2, lv47), out_sinfo=R.Tensor((1, 1, 4096), dtype="float16"))
            lv114 = R.call_tir(cls.slice1, (lv113,), out_sinfo=R.Tensor((1, 1, 4096), dtype="float16"))
            lv48: R.Tensor((512, 32000), dtype="uint32") = params[21]
            lv49: R.Tensor((128, 32000), dtype="float16") = params[22]
            lv5 = R.call_tir(cls.fused_decode3_fused_matmul5_cast2, (lv48, lv49, lv114), out_sinfo=R.Tensor((1, 1, 32000), dtype="float32"))
            gv1: R.Tuple(R.Tensor((1, 1, 32000), dtype="float32"), R.Tuple(R.Object, R.Object)) = lv5, (lv79, lv81)
            R.output(gv1)
        return gv1

    @R.function
    def encoding(input_ids: R.Tensor((1, "n"), dtype="int32"), all_seq_len: R.Shape(["m"]), kv_cache: R.Tuple(R.Object, R.Object), params: R.Tuple(R.Tensor((4096,), dtype="float16"), R.Tensor((4096,), dtype="float16"), R.Tensor((4096,), dtype="float16"), R.Tensor((2048, 128), dtype="float16"), R.Tensor((2048, 128), dtype="float16"), R.Tensor((32000, 512), dtype="uint32"), R.Tensor((32000, 128), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 4096), dtype="uint32"), R.Tensor((128, 4096), dtype="float16"), R.Tensor((512, 11008), dtype="uint32"), R.Tensor((128, 11008), dtype="float16"), R.Tensor((512, 11008), dtype="uint32"), R.Tensor((128, 11008), dtype="float16"), R.Tensor((1376, 4096), dtype="uint32"), R.Tensor((344, 4096), dtype="float16"), R.Tensor((512, 32000), dtype="uint32"), R.Tensor((128, 32000), dtype="float16"))) -> R.Tuple(R.Tensor((1, 1, 32000), dtype="float32"), R.Tuple(R.Object, R.Object)):
        n = T.int64()
        m = T.int64()
        R.func_attr({"tir_var_upper_bound": {"m": 2048, "n": 2048}})
        cls = Module
        with R.dataflow():
            lv = R.call_tir(cls.reshape5, (input_ids,), out_sinfo=R.Tensor((n,), dtype="int32"))
            lv_1: R.Tensor((32000, 512), dtype="uint32") = params[5]
            lv1: R.Tensor((32000, 128), dtype="float16") = params[6]
            lv1_1 = R.call_tir(cls.take_decode1, (lv_1, lv1, lv), out_sinfo=R.Tensor((n, 4096), dtype="float16"))
            lv2 = R.call_tir(cls.reshape6, (lv1_1,), out_sinfo=R.Tensor((1, n, 4096), dtype="float16"))
            lv9 = R.call_tir(cls.fused_min_max_triu_te_broadcast_to, R.tuple(), out_sinfo=R.Tensor((1, 1, n, n), dtype="float16"), tir_vars=R.shape([n]))
            lv5 = R.call_tir(cls.extend_te, (lv9,), out_sinfo=R.Tensor((1, 1, n, m), dtype="float16"))
            lv2_1: R.Tensor((4096,), dtype="float16") = params[0]
            lv6 = R.call_tir(cls.rms_norm, (lv2, lv2_1), out_sinfo=R.Tensor((1, n, 4096), dtype="float16"))
            lv3: R.Tensor((512, 4096), dtype="uint32") = params[7]
            lv4: R.Tensor((128, 4096), dtype="float16") = params[8]
            lv63 = R.call_tir(cls.decode4, (lv3, lv4), out_sinfo=R.Tensor((4096, 4096), dtype="float16"))
            lv1_2 = R.call_tir(cls.NT_matmul1, (lv6, lv63), out_sinfo=R.Tensor((1, n, 4096), dtype="float16"))
            lv9_1 = R.call_tir(cls.reshape7, (lv1_2,), out_sinfo=R.Tensor((1, n, 32, 128), dtype="float16"))
            lv5_1: R.Tensor((512, 4096), dtype="uint32") = params[9]
            lv6_1: R.Tensor((128, 4096), dtype="float16") = params[10]
            lv70 = R.call_tir(cls.decode4, (lv5_1, lv6_1), out_sinfo=R.Tensor((4096, 4096), dtype="float16"))
            lv2_2 = R.call_tir(cls.NT_matmul1, (lv6, lv70), out_sinfo=R.Tensor((1, n, 4096), dtype="float16"))
            lv12 = R.call_tir(cls.reshape7, (lv2_2,), out_sinfo=R.Tensor((1, n, 32, 128), dtype="float16"))
            lv7: R.Tensor((512, 4096), dtype="uint32") = params[11]
            lv8: R.Tensor((128, 4096), dtype="float16") = params[12]
            lv77 = R.call_tir(cls.decode4, (lv7, lv8), out_sinfo=R.Tensor((4096, 4096), dtype="float16"))
            lv3_1 = R.call_tir(cls.NT_matmul1, (lv6, lv77), out_sinfo=R.Tensor((1, n, 4096), dtype="float16"))
            lv15 = R.call_tir(cls.reshape7, (lv3_1,), out_sinfo=R.Tensor((1, n, 32, 128), dtype="float16"))
            lv9_2: R.Tensor((2048, 128), dtype="float16") = params[3]
            lv10: R.Tensor((2048, 128), dtype="float16") = params[4]
            lv16 = R.call_tir(cls.rotary_embedding, (lv9_1, lv9_2, lv10), out_sinfo=R.Tensor((1, n, 32, 128), dtype="float16"), tir_vars=R.shape([m]))
            lv11: R.Tensor((2048, 128), dtype="float16") = params[3]
            lv12_1: R.Tensor((2048, 128), dtype="float16") = params[4]
            lv17 = R.call_tir(cls.rotary_embedding, (lv12, lv11, lv12_1), out_sinfo=R.Tensor((1, n, 32, 128), dtype="float16"), tir_vars=R.shape([m]))
            lv18 = R.call_tir(cls.squeeze1, (lv17,), out_sinfo=R.Tensor((n, 32, 128), dtype="float16"))
            lv19 = R.call_tir(cls.squeeze1, (lv15,), out_sinfo=R.Tensor((n, 32, 128), dtype="float16"))
            lv20: R.Object = kv_cache[0]
            lv21: R.Object = R.call_packed("vm.builtin.attention_kv_cache_append", lv20, lv18, sinfo_args=(R.Object,))
            lv22: R.Object = kv_cache[1]
            lv23: R.Object = R.call_packed("vm.builtin.attention_kv_cache_append", lv22, lv19, sinfo_args=(R.Object,))
            lv24: R.Tensor((m, 32, 128), dtype="float16") = R.call_packed("vm.builtin.attention_kv_cache_view", lv21, R.shape([m, 32, 128]), sinfo_args=(R.Tensor((m, 32, 128), dtype="float16"),))
            lv25: R.Tensor((m, 32, 128), dtype="float16") = R.call_packed("vm.builtin.attention_kv_cache_view", lv23, R.shape([m, 32, 128]), sinfo_args=(R.Tensor((m, 32, 128), dtype="float16"),))
            lv26 = R.call_tir(cls.reshape3, (lv24,), out_sinfo=R.Tensor((1, m, 32, 128), dtype="float16"))
            lv27 = R.call_tir(cls.reshape3, (lv25,), out_sinfo=R.Tensor((1, m, 32, 128), dtype="float16"))
            lv28 = R.call_tir(cls.transpose2, (lv16,), out_sinfo=R.Tensor((1, 32, n, 128), dtype="float16"))
            lv29 = R.call_tir(cls.transpose2, (lv26,), out_sinfo=R.Tensor((1, 32, m, 128), dtype="float16"))
            lv30 = R.call_tir(cls.transpose2, (lv27,), out_sinfo=R.Tensor((1, 32, m, 128), dtype="float16"))
            lv10_1 = R.call_tir(cls.fused_NT_matmul2_divide2_maximum1_minimum1_cast3, (lv28, lv29, lv5), out_sinfo=R.Tensor((1, 32, n, m), dtype="float32"))
            lv11_1 = R.call_tir(cls.fused_softmax2_cast4, (lv10_1,), out_sinfo=R.Tensor((1, 32, n, m), dtype="float16"))
            lv39 = R.call_tir(cls.matmul8, (lv11_1, lv30), out_sinfo=R.Tensor((1, 32, n, 128), dtype="float16"))
            lv40 = R.call_tir(cls.transpose6, (lv39,), out_sinfo=R.Tensor((1, n, 32, 128), dtype="float16"))
            lv41 = R.call_tir(cls.reshape8, (lv40,), out_sinfo=R.Tensor((1, n, 4096), dtype="float16"))
            lv13: R.Tensor((512, 4096), dtype="uint32") = params[13]
            lv14: R.Tensor((128, 4096), dtype="float16") = params[14]
            lv84 = R.call_tir(cls.decode4, (lv13, lv14), out_sinfo=R.Tensor((4096, 4096), dtype="float16"))
            lv12_2 = R.call_tir(cls.fused_NT_matmul1_add1, (lv41, lv84, lv2), out_sinfo=R.Tensor((1, n, 4096), dtype="float16"))
            lv15_1: R.Tensor((4096,), dtype="float16") = params[1]
            lv45 = R.call_tir(cls.rms_norm, (lv12_2, lv15_1), out_sinfo=R.Tensor((1, n, 4096), dtype="float16"))
            lv16_1: R.Tensor((512, 11008), dtype="uint32") = params[15]
            lv17_1: R.Tensor((128, 11008), dtype="float16") = params[16]
            lv91 = R.call_tir(cls.decode5, (lv16_1, lv17_1), out_sinfo=R.Tensor((11008, 4096), dtype="float16"))
            lv13_1 = R.call_tir(cls.fused_NT_matmul3_silu1, (lv45, lv91), out_sinfo=R.Tensor((1, n, 11008), dtype="float16"))
            lv18_1: R.Tensor((512, 11008), dtype="uint32") = params[17]
            lv19_1: R.Tensor((128, 11008), dtype="float16") = params[18]
            lv98 = R.call_tir(cls.decode5, (lv18_1, lv19_1), out_sinfo=R.Tensor((11008, 4096), dtype="float16"))
            lv14_1 = R.call_tir(cls.fused_NT_matmul3_multiply1, (lv45, lv98, lv13_1), out_sinfo=R.Tensor((1, n, 11008), dtype="float16"))
            lv20_1: R.Tensor((1376, 4096), dtype="uint32") = params[19]
            lv21_1: R.Tensor((344, 4096), dtype="float16") = params[20]
            lv105 = R.call_tir(cls.decode6, (lv20_1, lv21_1), out_sinfo=R.Tensor((4096, 11008), dtype="float16"))
            lv15_2 = R.call_tir(cls.fused_NT_matmul4_add1, (lv14_1, lv105, lv12_2), out_sinfo=R.Tensor((1, n, 4096), dtype="float16"))
            lv22_1: R.Tensor((4096,), dtype="float16") = params[2]
            lv55 = R.call_tir(cls.rms_norm, (lv15_2, lv22_1), out_sinfo=R.Tensor((1, n, 4096), dtype="float16"))
            lv56 = R.call_tir(cls.slice, (lv55,), out_sinfo=R.Tensor((1, 1, 4096), dtype="float16"))
            lv23_1: R.Tensor((512, 32000), dtype="uint32") = params[21]
            lv24_1: R.Tensor((128, 32000), dtype="float16") = params[22]
            lv_2 = R.call_tir(cls.fused_decode3_fused_matmul5_cast2, (lv23_1, lv24_1, lv56), out_sinfo=R.Tensor((1, 1, 32000), dtype="float32"))
            gv: R.Tuple(R.Tensor((1, 1, 32000), dtype="float32"), R.Tuple(R.Object, R.Object)) = lv_2, (lv21, lv23)
            R.output(gv)
        return gv

    @R.function
    def softmax_with_temperature(logits: R.Tensor((1, 1, 32000), dtype="float32"), temperature: R.Tensor((), dtype="float32")) -> R.Tensor((1, 1, 32000), dtype="float32"):
        R.func_attr({"tir_var_upper_bound": {"m": 2048, "n": 2048}})
        cls = Module
        with R.dataflow():
            lv121 = R.call_tir(cls.divide, (logits, temperature), out_sinfo=R.Tensor((1, 1, 32000), dtype="float32"))
            lv122 = R.call_tir(cls.softmax, (lv121,), out_sinfo=R.Tensor((1, 1, 32000), dtype="float32"))
            gv3: R.Tensor((1, 1, 32000), dtype="float32") = lv122
            R.output(gv3)
        return gv3

# Metadata omitted. Use show_meta=True in script() method to show it.