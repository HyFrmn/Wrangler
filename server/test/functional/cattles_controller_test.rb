require 'test_helper'

class CattlesControllerTest < ActionController::TestCase
  test "should get index" do
    get :index
    assert_response :success
    assert_not_nil assigns(:cattles)
  end

  test "should get new" do
    get :new
    assert_response :success
  end

  test "should create cattle" do
    assert_difference('Cattle.count') do
      post :create, :cattle => { }
    end

    assert_redirected_to cattle_path(assigns(:cattle))
  end

  test "should show cattle" do
    get :show, :id => cattles(:one).to_param
    assert_response :success
  end

  test "should get edit" do
    get :edit, :id => cattles(:one).to_param
    assert_response :success
  end

  test "should update cattle" do
    put :update, :id => cattles(:one).to_param, :cattle => { }
    assert_redirected_to cattle_path(assigns(:cattle))
  end

  test "should destroy cattle" do
    assert_difference('Cattle.count', -1) do
      delete :destroy, :id => cattles(:one).to_param
    end

    assert_redirected_to cattles_path
  end
end
