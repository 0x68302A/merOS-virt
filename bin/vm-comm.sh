#!/bin/bash



source_vm_comm() {

	export SSH_KEY=$MOS_PATH/etc/ssh-keys/$VM_ID-id_rsa
	export SSHD_TARGET=${MACH_VAR[USER_NAME]}@${MACH_NET[ADDRESS]}
	export SSHD_PORT=${MACH_SSH[LISTEN_PORT]}

	mkdir -p $MOS_PATH/mos-shared/$VM_ID/
}


ssh_connect() {

	source_vm_var
	source_vm_comm

        sudo -u $USER_ID \
        ssh -p $SSHD_PORT $SSHD_TARGET -i $SSH_KEY -Y
}

ssh_push() {

	source_vm_var
	source_vm_comm

        sudo -u $USER_ID \
        rsync -rzP --append -e "ssh -p $SSHD_PORT -i $SSH_KEY" \
        $FILE \
        $SSHD_TARGET:/home/user/mos-temp/

}

ssh_pull() {

	source_vm_var
	source_vm_comm

        sudo -u $USER_ID \
        rsync -rzP --append -e "ssh -p $SSHD_PORT -i $SSH_KEY" \
        $SSHD_TARGET:/home/user/mos-shared/* \
        $MOS_PATH/mos-shared/$VM_ID/


}

ssh_sync() {

	source_vm_var
	source_vm_comm

	ssh_pull

        sudo -u $USER_ID \
        rsync -rzP --append -e "ssh -p $SSHD_PORT -i $SSH_KEY" \
        $MOS_PATH/mos-shared/$VM_ID/* \
	$SSHD_TARGET:/home/user/mos-shared/

}
