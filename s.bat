# PWD0=$PWD; cd              <rel_path_to_submodule>             ; bash sync.bat; cd $PWD0;

echo ""
echo "SUBMODULE  ---->  $PWD  <----  "

git add --all .
git commit -m sync_bat -a
git pull --no-edit --prune origin
git pull --tags    --prune origin

git add --all .
git commit -m automatic_merge_after_pull -a
git push -u     origin HEAD
git push --tags origin

echo ""
echo "======================="
echo ""

exit 

