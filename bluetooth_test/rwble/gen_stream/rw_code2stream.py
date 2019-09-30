#! python3
import os
from collections import OrderedDict

__all__ = [
    'code2stream'
]

path_rwble_base = r'E:\work\svn_ble_lib\trunk\rwble'
path_gcc = r'c:/Program Files (x86)/Dev-Cpp/MinGW64/bin/gcc.exe'
release_marco = r'CONFIG_HS6621A1_RELEASE'


def check_env():
    if not os.path.exists(path_rwble_base):
        raise Exception('%s not exist.' % path_rwble_base)
    if not os.path.exists(path_gcc):
        raise Exception('%s not exist.' % path_gcc)


def code2stream(code_list):
    check_env()
    c_template_begin = r'''
        #include <stdio.h>
        #include <stdlib.h>
        #include <string.h>
        #include <stdint.h>
        #include "compiler.h"
        #include "stack/ip/ble/hl/api/att.h"
        #include "stack/ip/ble/hl/api/gap.h"
        #include "stack/ip/ble/hl/api/gapc_task.h"
        #include "stack/ip/ble/hl/api/gapm_task.h"
        #include "stack/ip/ble/hl/api/gattc_task.h"
        #include "stack/ip/ble/hl/api/gattm_task.h"
        #include "stack/ip/ble/hl/api/l2cc_task.h"
        #include "stack/ip/ble/hl/api/l2cc_task.h"
        #include "stack/ip/ble/hl/api/prf_types.h"
        #include "stack/ip/ble/hl/api/rwble_hl_error.h"
        #include "stack/modules/common/api/co_bt_defines.h"
        #include "stack/modules/ke/api/ke_msg.h"
        #include "stack/ip/ble/ll/api/rwble_config.h"
        #include "stack/modules/rwip/api/rwip_config.h"

        void dump(void *data)
        {
            int i;
            struct ke_msg *p = ke_param2msg(data);
            printf("05 ");
            uint16_t dest_map[] = {TASK_ID_LLM, TASK_ID_LLC, TASK_ID_DBG, TASK_ID_APP, TASK_ID_L2CC, TASK_ID_GATTM, TASK_ID_GATTC, TASK_ID_GAPM, TASK_ID_GAPC};
            p->dest_id = p->dest_id<sizeof(dest_map)/sizeof(dest_map[0])?dest_map[p->dest_id]:p->dest_id;
            if(p->dest_id == TASK_AHI) p->dest_id = TASK_ID_AHI;
            p->src_id = p->src_id<sizeof(dest_map)/sizeof(dest_map[0])?dest_map[p->src_id]:p->src_id;
            if(p->src_id == TASK_AHI) p->src_id = TASK_ID_AHI;
            for(i=0;i<p->param_len+8;i++){ printf("%02x ", ((uint8_t*)&p->id)[i]); }
            printf("\n");
        }

        void *ke_msg_alloc(ke_msg_id_t const id, ke_task_id_t const dest_id,
                           ke_task_id_t const src_id, uint16_t const param_len)
        {
            struct ke_msg *msg = (struct ke_msg*) calloc(1, sizeof(struct ke_msg) + param_len);
            void *param_ptr = NULL;
            ASSERT_ERR(msg != NULL);
            msg->hdr.next  = 0;
            msg->id        = id;
            msg->dest_id   = dest_id;
            msg->src_id    = src_id;
            msg->param_len = param_len;
            param_ptr = ke_msg2param(msg);
            memset(param_ptr, 0, param_len);
            return param_ptr;
        }
        #define KE_MSG_ALLOC_DYN(id, dest, src, param_str,length)  (struct param_str*)ke_msg_alloc(id, dest, src, \
            (sizeof(struct param_str) + (length)));

        int main(int argc, char *argv[]) {
    '''
    c_template_end = r'''
        }
    '''
    split_flag = '__S_P_L_I_T__F_L_A_G__'
    c_inc_path = r'''
        /
        /hardware/sys
        /hardware/cmsis
        /stack/modules/common/api
        /stack/modules/rwip/api
        /stack/modules/ke/api
        /stack/plf/hs6621/arch
        /stack/app/api
        /stack/plf/hs6621/sc
        /stack/ip/ble/ll/api
        /stack/ip/ble/hl/inc
        /stack/ip/ble/hl/api
        /include
    '''
    c_filename = 'tmp.c'
    output_name = 'out.exe'
    if os.path.exists(output_name):
        os.remove(output_name)
    with open(c_filename, 'w') as f:
        c_code = c_template_begin
        if isinstance(code_list, OrderedDict):
            for k, code in code_list.items(): c_code += '{%sprintf("%s");}' % (code, split_flag)
        else:
            for code in code_list: c_code += '{%sprintf("%s");}' % (code, split_flag)
        c_code += c_template_end
        f.write(c_code)
        f.close()
    compile_command = '"{}" -D{} {} -o {} -w'.format(path_gcc, release_marco, c_filename, output_name)
    for p in c_inc_path.strip().split('\n'):
        compile_command += ' -I{}{}'.format(path_rwble_base, p.strip())
    # print(compile_command)
    os.popen(compile_command).read()
    if not os.path.exists(output_name):
        raise Exception('Compile source code failed.')
    _output = os.popen(output_name)
    ret = [o.strip() for o in _output.read().split(split_flag)]
    if os.path.exists(c_filename):
        os.remove(c_filename)
    if os.path.exists(output_name):
        os.remove(output_name)
    if isinstance(code_list, OrderedDict):
        ret_dict = OrderedDict()
        for k, v in zip(code_list, ret):
            ret_dict[k] = v
        return ret_dict
    else:
        return ret


if __name__ == '__main__':
    code_list = [
        r'''
            struct gapm_reset_cmd *msg = KE_MSG_ALLOC(GAPM_RESET_CMD, TASK_GAPM, TASK_APP, gapm_reset_cmd);
            msg->operation = GAPM_RESET;
            dump(msg);
        ''',
    ]
    for stream in code2stream(code_list):
        print(stream)
